from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, InaccessibleMessage, TelegramObject, Update

from date_task_bot.presentation.utils import DateFormatter, KeyboardBuilder
from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
    UserSettingsRepository,
)
from date_task_bot.use_cases import (
    CreateTaskUseCase,
    GetTimezoneUseCase,
    ParseDateTimeUseCase,
    SetTimezoneUseCase,
)


class DIMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker):
        super().__init__()
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

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
        chat_id = None
        if isinstance(event, Update):
            if event.message:
                chat_id = event.message.chat.id
            elif event.callback_query:
                chat_id = event.callback_query.message.chat.id  # type: ignore
            else:
                # TODO: LOGGING, handle
                pass
        else:
            # TODO: LOGGING, handle
            pass

        data["chat_id"] = str(chat_id)

        # use cases
        data["get_tz_uc"] = GetTimezoneUseCase(user_settings_repo=user_settings_repo)
        data["set_tz_uc"] = SetTimezoneUseCase(user_settings_repo=user_settings_repo)
        data["parse_datetime_uc"] = ParseDateTimeUseCase()
        data["create_task_uc"] = CreateTaskUseCase(
            task_repo=task_repo, user_settings_repo=user_settings_repo
        )

        # presentation utils
        data["date_formatter"] = DateFormatter()

        return await handler(event, data)


class CallbackMessageMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if event.message is None:
            await event.answer("Сообщение не найдено", show_alert=True)
            return

        if isinstance(event.message, InaccessibleMessage):
            bot: Bot = data.get("bot")  # type: ignore
            if bot:
                await bot.send_message(
                    chat_id=event.message.chat.id,
                    text="Сообщение недоступно",
                )
            await event.answer()
            return

        return await handler(event, data)
