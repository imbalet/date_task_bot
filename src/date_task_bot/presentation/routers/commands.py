from typing import cast

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from date_task_bot.presentation.constants import TEXTS, MsgKey
from date_task_bot.presentation.constants.templates import TimezoneTemplate
from date_task_bot.presentation.formatters.messages import (
    StartCommandMessageFormatter,
    TimezoneCommandMessageFormatter,
    TimezoneSetMessageFormatter,
)
from date_task_bot.presentation.states import TimezoneSelectionState
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.repositories.schemas import UserCreate
from date_task_bot.use_cases import (
    GetTimezoneUseCase,
    RegisterUserUseCase,
    SetTimezoneUseCase,
)

router = Router(name=__name__)


class TimeZoneCallback(CallbackData, prefix="tz"):
    tz: str


@router.message(Command("start"))
async def start(
    message: Message,
    state: FSMContext,
    user_id: str,
    register_user_uc: RegisterUserUseCase,
):
    register_user_res = await register_user_uc.execute(data=UserCreate(id=user_id))

    timezone_text = ""
    if register_user_res.user.settings:
        timezone_text = TimezoneTemplate(
            timezone=register_user_res.user.settings.timezone
        ).render()

    text = StartCommandMessageFormatter().format(formatted_timezone=timezone_text)

    await update_main_message(
        state=state,
        event=message,
        text=text,
        create_new=True,
    )


@router.message(Command("timezone"))
async def set_timezone(
    message: Message,
    state: FSMContext,
    user_id: str,
    kbr_builder: KeyboardBuilder,
    get_tz_uc: GetTimezoneUseCase,
):
    get_user_tz_res = await get_tz_uc.execute(user_id=user_id)

    popular_zones = ["Europe/Moscow", "Europe/London", "Asia/Tokyo", "America/New_York"]
    for tz in popular_zones:
        kbr_builder.button_text(tz, callback_data=TimeZoneCallback(tz=tz))
    kbr_builder.button(MsgKey.OTHER_TZ, callback_data=TimeZoneCallback(tz="other"))

    text = TimezoneCommandMessageFormatter().format(
        timezone=get_user_tz_res.current_timezone,
        time=get_user_tz_res.current_time.strftime("%H:%M"),
    )

    await update_main_message(
        state=state,
        event=message,
        text=text,
        reply_markup=kbr_builder.as_markup(),
        create_new=True,
    )


@router.message(TimezoneSelectionState.AWAIT_TZ_NAME)
@router.callback_query(TimeZoneCallback.filter())
async def set_timezone_callback(
    event: Message | CallbackQueryWithMessage,
    *,
    callback_data: TimeZoneCallback | None = None,
    state: FSMContext,
    user_id: str,
    set_tz_uc: SetTimezoneUseCase,
):
    if isinstance(event, CallbackQuery) and callback_data:
        tz = callback_data.tz
    else:
        event = cast(Message, event)
        await state.set_state()
        tz = str(event.text).strip()

    if tz == "other":
        await state.set_state(TimezoneSelectionState.AWAIT_TZ_NAME)
        text = TEXTS[MsgKey.SEND_YOUR_TIMEZONE]
    else:
        set_tz_res = await set_tz_uc.execute(user_id=user_id, tz=tz)

        if set_tz_res.success and set_tz_res.current_time:
            text = TimezoneSetMessageFormatter().format(
                timezone=tz, time=set_tz_res.current_time.strftime("%H:%M")
            )
        else:
            text = TEXTS[MsgKey.NO_TIMEZONE]

    await update_main_message(
        state=state,
        event=event,
        text=text,
    )
