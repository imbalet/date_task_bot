from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.constants import TEXTS, MsgKey
from date_task_bot.presentation.formatters.messages import CreatedTaskMessageFormatter
from date_task_bot.presentation.formatters.models import TaskFormatter
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

    parsed_date = parse_datetime_uc.execute(
        user_tz_str=user_tz_data.current_timezone, text=text
    )

    if not parsed_date.date or not parsed_date.text:
        text = TEXTS[MsgKey.DATE_OR_TEXT_NOT_FOUND]
    else:
        created_task = await create_task_uc.execute(
            user_id=chat_id, text=parsed_date.text, due_date=parsed_date.date
        )
        task_formatter = TaskFormatter(user_tz=user_tz_data.current_timezone)
        formatted_task = task_formatter.format(created_task.task)

        text = CreatedTaskMessageFormatter().format(formatted_task=formatted_task)

    await update_main_message(
        state=state,
        event=message,
        text=text,
        create_new=True,
    )
