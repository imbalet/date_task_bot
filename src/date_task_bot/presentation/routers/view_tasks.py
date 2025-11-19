from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.constants import TEXTS
from date_task_bot.presentation.constants.text import MsgKey
from date_task_bot.presentation.formatters.messages import AllTasksMessageFormatter
from date_task_bot.presentation.formatters.models import TaskListFormatter
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.repositories.schemas import TaskPaginationRequest
from date_task_bot.use_cases import (
    GetAllTasksUseCase,
    GetTimezoneUseCase,
)

router = Router(name=__name__)


class TaskCallback(CallbackData, prefix="task"):
    task: UUID


class TaskControlCallback(CallbackData, prefix="task_c"):
    page: int


@router.callback_query(TaskControlCallback.filter())
@router.message(Command("tasks"))
async def all_tasks(
    event: Message | CallbackQueryWithMessage,
    *,
    callback_data: TaskControlCallback | None = None,
    state: FSMContext,
    chat_id: str,
    get_all_tasks_uc: GetAllTasksUseCase,
    get_tz_uc: GetTimezoneUseCase,
    kbr_builder: KeyboardBuilder,
):
    current_page = 1
    if callback_data:
        current_page = callback_data.page

    user_tz_data = await get_tz_uc.execute(user_id=chat_id)
    res = await get_all_tasks_uc.execute(
        TaskPaginationRequest(user_id=chat_id, page=current_page, page_size=6)
    )
    tasks_formatter = TaskListFormatter(user_tz=user_tz_data.current_timezone)
    formatted_task_list = tasks_formatter.format(res)

    if formatted_task_list:
        text = AllTasksMessageFormatter().format(
            formatted_task_list=formatted_task_list
        )
    else:
        text = TEXTS[MsgKey.NO_TASKS]

    extra_buttons = []
    if current_page > 1:
        extra_buttons.append((MsgKey.PREV, TaskControlCallback(page=current_page - 1)))
    if current_page < res.total_pages:
        extra_buttons.append((MsgKey.NEXT, TaskControlCallback(page=current_page + 1)))

    kbr_builder.conf(row_width=2, extra_buttons=extra_buttons)
    kbr_builder.buttons_text_tuple(
        *[
            (str(idx), TaskCallback(task=el.id))
            for idx, el in enumerate(res.items, start=res.offset + 1)
        ]
    )

    await update_main_message(
        state=state,
        event=event,
        text=text,
        reply_markup=kbr_builder.as_markup(),
        create_new=isinstance(event, Message),
    )
