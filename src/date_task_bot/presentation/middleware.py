from collections.abc import Awaitable, Callable
from logging import getLogger
from typing import Any, cast

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, InaccessibleMessage, TelegramObject, Update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from date_task_bot.presentation.utils import KeyboardBuilder
from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
    UserSettingsRepository,
)
from date_task_bot.use_cases import (
    ChangeTaskStatusUseCase,
    CreateTaskUseCase,
    DeleteTaskUseCase,
    EditTaskUseCase,
    GetAllTasksUseCase,
    GetTaskUseCase,
    GetTimezoneUseCase,
    MarkAsDoneUseCase,
    ParseDatetimeFromTextUseCase,
    ParseDateTimeUseCase,
    RegisterUserUseCase,
    SetTimezoneUseCase,
)

logger = getLogger(__name__)


class DIMiddleware[T](BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[T]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> T | None:

        # DB, repositories
        user_repo = UserRepository(session_factory=self.sessionmaker)
        user_settings_repo = UserSettingsRepository(session_factory=self.sessionmaker)
        task_repo = TaskRepository(session_factory=self.sessionmaker)
        reminder_repo = ReminderRepository(session_factory=self.sessionmaker)

        data["sessionmaker"] = self.sessionmaker
        data["reminder_repository"] = reminder_repo
        data["task_repository"] = task_repo
        data["user_repository"] = user_repo
        data["user_settings_repository"] = user_settings_repo
        data["kbr_builder"] = KeyboardBuilder()

        # utils
        user_id = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                # TODO: change to user id
                user_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user.id:
                user_id = event.callback_query.from_user.id
            else:
                logger.error(f"No user id found in event {type(event)}")
                return None
        else:
            logger.error(f"Unknown event type {type(event)}")
            return None

        data["user_id"] = str(user_id)

        # use cases
        data["get_tz_uc"] = GetTimezoneUseCase(user_settings_repo=user_settings_repo)
        data["set_tz_uc"] = SetTimezoneUseCase(user_settings_repo=user_settings_repo)
        data["parse_datetime_uc"] = ParseDateTimeUseCase()
        data["parse_datetime_from_text_uc"] = ParseDatetimeFromTextUseCase()
        data["create_task_uc"] = CreateTaskUseCase(
            task_repo=task_repo, user_settings_repo=user_settings_repo
        )
        data["register_user_uc"] = RegisterUserUseCase(user_repo=user_repo)
        data["get_all_tasks_uc"] = GetAllTasksUseCase(task_repo=task_repo)
        data["get_task_uc"] = GetTaskUseCase(task_repo=task_repo)
        data["delete_task_uc"] = DeleteTaskUseCase(task_repo=task_repo)
        data["edit_task_uc"] = EditTaskUseCase(
            task_repo=task_repo, reminder_repo=reminder_repo
        )
        data["change_status_uc"] = ChangeTaskStatusUseCase(task_repo=task_repo)
        data["mark_as_done_uc"] = MarkAsDoneUseCase(
            task_repo=task_repo, reminder_repo=reminder_repo
        )

        return await handler(event, data)


class CallbackMessageMiddleware[T](BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[T]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> T | None:
        if not isinstance(event, CallbackQuery):
            return await handler(cast(CallbackQuery, event), data)

        if event.message is None:
            await event.answer("Сообщение не найдено", show_alert=True)
            return None

        if isinstance(event.message, InaccessibleMessage):
            bot = data.get("bot")
            bot = cast(Bot, bot)
            if bot:
                await bot.send_message(
                    chat_id=event.message.chat.id,
                    text="Сообщение недоступно",
                )
            await event.answer()
            return None

        return await handler(event, data)
