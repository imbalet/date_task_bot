from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.utils import update_main_message
from date_task_bot.use_cases import (
    CreateTaskUseCase,
    GetTimezoneUseCase,
    ParseDateTimeUseCase,
)

router = Router(name=__name__)


@router.message(F.text)
async def start_adding_task(
    message: Message,
    state: FSMContext,
    chat_id: str,
    get_tz_uc: GetTimezoneUseCase,
    parse_datetime_uc: ParseDateTimeUseCase,
    create_task_uc: CreateTaskUseCase,
) -> None:
    text = str(message.text).strip()

    user_tz_data = await get_tz_uc.execute(user_id=chat_id)
    res = parse_datetime_uc.execute(user_tz=user_tz_data.current_timezone, text=text)

    if not res.date or not res.text:
        text = "Не найдена дата или текст."
    else:
        res = await create_task_uc.execute(
            user_id=chat_id, text=res.text, due_date=res.date
        )
        text = (
            f"Создана задача\n`{res.task.text}`\n c датой {res.task.due_date} и напоминаниями в\n"
            + "\n".join([str(i.remind_at) for i in res.reminders])
        )

    await update_main_message(state=state, message=message, text=text, create_new=True)
