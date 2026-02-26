from logging import getLogger
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InaccessibleMessage,
    InlineKeyboardMarkup,
    MaybeInaccessibleMessageUnion,
    Message,
)

from date_task_bot.presentation.utils import CallbackQueryWithMessage

logger = getLogger(__name__)


async def update_main_message(
    state: FSMContext,
    event: MaybeInaccessibleMessageUnion | CallbackQueryWithMessage,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    create_new: bool = False,
    **kwargs: Any,  # noqa: ANN401
) -> None:
    if isinstance(event, InaccessibleMessage):
        bot = event.bot
        if bot:
            await bot.send_message(
                chat_id=event.chat.id,
                text="Сообщение недоступно",
            )
        return
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
        await event.answer()

    data = await state.get_data()
    main_message_id = data.get("main_message_id")

    if main_message_id and message.bot and not create_new:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=main_message_id,
                text=text,
                reply_markup=reply_markup,
                **kwargs,
            )
            if main_message_id != message.message_id:
                await message.delete()
            return
        except Exception:
            logger.warning("error to send message", stacklevel=2)
            pass

    msg = await message.answer(text=text, reply_markup=reply_markup, **kwargs)
    await state.update_data(main_message_id=msg.message_id)
