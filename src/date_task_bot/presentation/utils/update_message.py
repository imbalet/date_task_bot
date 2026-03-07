from logging import getLogger
from typing import Any, Protocol

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InaccessibleMessage,
    InlineKeyboardMarkup,
    MaybeInaccessibleMessageUnion,
    Message,
)

from date_task_bot.presentation.services import Sender
from date_task_bot.presentation.utils import CallbackQueryWithMessage

logger = getLogger(__name__)


class UpdateMainMessage(Protocol):
    async def __call__(
        self,
        state: FSMContext,
        event: MaybeInaccessibleMessageUnion | CallbackQueryWithMessage,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        create_new: bool = False,
        **kwargs: Any,
    ) -> None: ...


async def update_main_message(
    sender: Sender,
    state: FSMContext,
    event: MaybeInaccessibleMessageUnion | CallbackQueryWithMessage,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    create_new: bool = False,
    **kwargs: Any,
) -> None:
    if isinstance(event, InaccessibleMessage):
        await sender.send_message(
            event.chat.id,
            "Сообщение недоступно",
        )
        return
    if isinstance(event, Message):
        message = event
        is_user_message = True
    else:
        message = event.message
        is_user_message = False
        await event.answer()

    data = await state.get_data()
    main_message_id = data.get("main_message_id")

    target_message_id = main_message_id
    if (
        main_message_id
        and not isinstance(event, Message)
        and message.message_id != main_message_id
    ):
        target_message_id = message.message_id

    if target_message_id and not create_new:
        try:
            await sender.edit_message(
                chat_id=message.chat.id,
                message_id=target_message_id,
                text=text,
                reply_markup=reply_markup,
                **kwargs,
            )

            if is_user_message:
                await message.delete()
            return
        except Exception:
            logger.exception("failed to edit main message")

    msg = await sender.answer_message(
        message,
        text=text,
        reply_markup=reply_markup,
        **kwargs,
    )

    if msg:
        await state.update_data(main_message_id=msg.message_id)
