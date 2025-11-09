from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.states import TimezoneSelectionState
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.repositories import UserRepository
from date_task_bot.repositories.schemas import UserCreate
from date_task_bot.use_cases import GetTimezoneUseCase, SetTimezoneUseCase

router = Router(name=__name__)


class TimeZoneCallback(CallbackData, prefix="tz"):
    tz: str


@router.message(Command("start"))
async def start(
    message: Message,
    user_repository: UserRepository,
    state: FSMContext,
):
    await user_repository.create(UserCreate(id=str(message.chat.id)))
    await update_main_message(
        state=state, message=message, text="Привет, это бот для задач", create_new=True
    )


@router.message(Command("timezone"))
async def set_timezone(
    message: Message,
    state: FSMContext,
    user_repository: UserRepository,
    chat_id: str,
    kbr_builder: KeyboardBuilder,
):
    uc = GetTimezoneUseCase(user_repo=user_repository)
    user_tz = await uc.execute(user_id=chat_id)

    popular_zones = ["Europe/Moscow", "Europe/London", "Asia/Tokyo", "America/New_York"]
    for tz in popular_zones:
        kbr_builder.button_text(tz, callback_data=TimeZoneCallback(tz=tz))
    kbr_builder.button_text("Другая", callback_data=TimeZoneCallback(tz="other"))

    await update_main_message(
        state=state,
        message=message,
        text=(
            f"Выберите свой часовой пояс. Текущий часовой пояс: {user_tz.current_timezone},"
            f"текущее время: {user_tz.current_time}."
        ),
        reply_markup=kbr_builder.as_markup(),
        create_new=True,
    )


@router.callback_query(TimeZoneCallback.filter())
async def set_timezone_callback(
    callback: CallbackQueryWithMessage,
    callback_data: TimeZoneCallback,
    state: FSMContext,
    chat_id: str,
    user_repository: UserRepository,
):
    tz = callback_data.tz
    if tz == "other":
        await state.set_state(TimezoneSelectionState.AWAIT_TZ_NAME)
        text = "Напишите ваш часовой пояс по стандарту IANA."
    else:
        uc = SetTimezoneUseCase(user_repo=user_repository)
        res = await uc.execute(user_id=chat_id, tz=tz)

        if res.success and res.current_time:
            text = f"Часовой пояс установлен: {tz}\nТекущее время: {res.current_time.strftime('%H:%M')}"
        else:
            text = "Такого часового пояса нет. Попробуйте выбрать из списка популярных или напишите корректно."

    await update_main_message(state=state, message=callback.message, text=text)


@router.message(TimezoneSelectionState.AWAIT_TZ_NAME)
async def set_timezone_message(
    message: Message,
    state: FSMContext,
    chat_id: str,
    user_repository: UserRepository,
):
    await state.set_state()
    tz = str(message.text).strip()
    uc = SetTimezoneUseCase(user_repo=user_repository)
    res = await uc.execute(user_id=chat_id, tz=tz)

    if res.success and res.current_time:
        text = f"Часовой пояс установлен: {tz}\nТекущее время: {res.current_time.strftime('%H:%M')}"
    else:
        text = "Такого часового пояса нет. Попробуйте выбрать из списка популярных или напишите корректно."

    await update_main_message(state=state, message=message, text=text)
