from logging import getLogger
from typing import cast

from aiogram.client.bot import Bot
from aiogram.types import ErrorEvent, Update

from date_task_bot.exceptions import (
    AlreadyExistsException,
    AppException,
    EntityEnum,
    NotFoundException,
    ValidationException,
)
from date_task_bot.presentation.constants import TEXTS, MsgKey

logger = getLogger(__name__)

ENTITY_TO_MSG_KEY = {
    EntityEnum.USER: MsgKey.USER,
    EntityEnum.TASK: MsgKey.TASK,
    EntityEnum.SETTINGS: MsgKey.USER_SETTINGS,
    EntityEnum.REMINDER: MsgKey.REMINDER,
    EntityEnum.OTHER: MsgKey.OTHER_ENTITY,
}


def get_chat_info(update: Update) -> tuple[int | None, Bot | None]:
    user_id = None
    bot = None
    if update.message and update.message.from_user:
        user_id = update.message.from_user.id
        bot = update.message.bot
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
        bot = update.callback_query.bot
    return user_id, bot


async def app_exceptions_handler(event: ErrorEvent) -> bool:
    user_id, bot = get_chat_info(event.update)
    exception = event.exception
    exception = cast(AppException, exception)

    logger.exception(
        "AppException handled: type=%s entity=%s data=%s",
        type(exception).__name__,
        exception.entity,
        exception.data,
    )

    entity_str = TEXTS[ENTITY_TO_MSG_KEY.get(exception.entity, MsgKey.OTHER_ENTITY)]

    if user_id and bot:
        match exception:
            case NotFoundException():
                await bot.send_message(
                    user_id,
                    TEXTS[MsgKey.NOT_FOUND_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case AlreadyExistsException():
                await bot.send_message(
                    user_id,
                    TEXTS[MsgKey.ALREADY_EXISTS_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case ValidationException():
                await bot.send_message(
                    user_id,
                    TEXTS[MsgKey.VALIDATION_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case _:
                await bot.send_message(user_id, TEXTS[MsgKey.UNEXPECTED_ERROR])
    return True
