from aiogram.types import CallbackQuery, Message


class CallbackQueryWithMessage(CallbackQuery):
    message: Message  # pyright: ignore[reportGeneralTypeIssues]
