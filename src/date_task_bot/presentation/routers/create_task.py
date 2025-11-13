from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.utils import DateFormatter, update_main_message
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
    date_formatter: DateFormatter,
) -> None:
    text = str(message.text).strip()

    user_tz_data = await get_tz_uc.execute(user_id=chat_id)
    date_formatter.set_timezone(user_tz_data.current_timezone)
    parsed_date = parse_datetime_uc.execute(
        user_tz_str=user_tz_data.current_timezone, text=text
    )

    if not parsed_date.date or not parsed_date.text:
        text = "Не найдена дата или текст."
    else:
        created_task = await create_task_uc.execute(
            user_id=chat_id, text=parsed_date.text, due_date=parsed_date.date
        )
        formatted_due_date = date_formatter.format_date_long(created_task.task.due_date)
        # TODO: highlight dates in the message.
        # if the day of the reminder coincides with the day of the task, show only time
        text = (
            f"Создана задача\n`{created_task.task.text}`\n c датой {formatted_due_date} и напоминаниями в\n"
            + "\n".join(
                [
                    date_formatter.format_date_short(i.remind_at)
                    for i in created_task.task.reminders
                ]
            )
        )

    await update_main_message(state=state, message=message, text=text, create_new=True)
