from typing import cast

from aiogram.types import ErrorEvent, Update

from date_task_bot.exceptions import (
    AlreadyExistsException,
    AppException,
    EntityEnum,
    NotFoundException,
    ValidationException,
)
from date_task_bot.presentation.constants import TEXTS, MsgKey

ENTITY_TO_MSG_KEY = {
    EntityEnum.USER: MsgKey.USER,
    EntityEnum.TASK: MsgKey.TASK,
    EntityEnum.SETTINGS: MsgKey.USER_SETTINGS,
    EntityEnum.REMINDER: MsgKey.REMINDER,
    EntityEnum.OTHER: MsgKey.OTHER_ENTITY,
}


def get_chat_info(update: Update):
    chat_id = None
    bot = None
    if update.message:
        chat_id = update.message.chat.id
        bot = update.message.bot
    elif update.callback_query and update.callback_query.message:
        chat_id = update.callback_query.message.chat.id
        bot = update.callback_query.message.bot
    return chat_id, bot


async def app_exceptions_handler(event: ErrorEvent):
    chat_id, bot = get_chat_info(event.update)
    exception = event.exception
    exception = cast(AppException, exception)

    entity_str = TEXTS[ENTITY_TO_MSG_KEY.get(exception.entity, MsgKey.OTHER_ENTITY)]

    if chat_id and bot:
        match exception:
            case NotFoundException():
                await bot.send_message(
                    chat_id,
                    TEXTS[MsgKey.NOT_FOUND_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case AlreadyExistsException():
                await bot.send_message(
                    chat_id,
                    TEXTS[MsgKey.ALREADY_EXISTS_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case ValidationException():
                await bot.send_message(
                    chat_id,
                    TEXTS[MsgKey.VALIDATION_ERROR].format(
                        entity=entity_str, data=exception._format_data(exception.data)
                    ),
                )
            case _:
                await bot.send_message(chat_id, TEXTS[MsgKey.UNEXPECTED_ERROR])
    # logging here
    return True
