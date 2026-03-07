import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.methods.delete_webhook import DeleteWebhook
from aiogram.types import BotCommand

from date_task_bot.config import get_config
from date_task_bot.database import create_tables, get_sessionmaker
from date_task_bot.exceptions import AppException
from date_task_bot.exceptions_handler import app_exceptions_handler
from date_task_bot.healthcheck import start_healthcheck_server
from date_task_bot.logger import setup_logger
from date_task_bot.presentation.middleware import (
    CallbackMessageMiddleware,
    DIMiddleware,
)
from date_task_bot.presentation.routers import (
    commands_router,
    create_task_router,
    task_actions_router,
    view_tasks_router,
)
from date_task_bot.presentation.services import Sender
from date_task_bot.reminder import Reminder
from date_task_bot.repositories import ReminderRepository

setup_logger()


async def main() -> None:

    dp = Dispatcher()

    dp.errors.register(app_exceptions_handler, ExceptionTypeFilter(AppException))

    dp.callback_query.middleware(CallbackMessageMiddleware())

    bot = Bot(
        token=get_config().BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/timezone", description="Смена часового пояса"),
        BotCommand(command="/tasks", description="Список задач"),
    ]  # TODO: move it
    await bot.set_my_commands(commands)

    await bot(DeleteWebhook(drop_pending_updates=True))
    dp.include_router(commands_router)
    dp.include_router(view_tasks_router)
    dp.include_router(task_actions_router)
    dp.include_router(create_task_router)

    engine, sessionmaker = await get_sessionmaker()
    await create_tables(engine)

    sender = Sender(bot=bot)
    dp.update.middleware(DIMiddleware(sessionmaker, sender=sender))

    reminder_repo = ReminderRepository(sessionmaker)
    reminder = Reminder(bot=bot, sender=sender, reminder_repo=reminder_repo)
    await reminder.start()

    health_task = asyncio.create_task(start_healthcheck_server(8000))

    await dp.start_polling(bot)

    # shutdown
    await reminder.stop()
    await engine.dispose()
    health_task.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
