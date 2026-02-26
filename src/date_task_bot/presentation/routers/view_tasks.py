from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.callbacks import (
    TaskAction,
    TaskActionCallback,
    TaskCallback,
    TaskPaginationCallback,
)
from date_task_bot.presentation.constants import TEXTS, MsgKey
from date_task_bot.presentation.formatters.messages import AllTasksMessageFormatter
from date_task_bot.presentation.formatters.models import (
    TaskFormatter,
    TaskListFormatter,
)
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.repositories.schemas import TaskPaginationRequest
from date_task_bot.use_cases import (
    GetAllTasksUseCase,
    GetTaskUseCase,
    GetTimezoneUseCase,
)

router = Router(name=__name__)


@router.callback_query(TaskPaginationCallback.filter())
@router.message(Command("tasks"))
async def all_tasks(
    event: Message | CallbackQueryWithMessage,
    *,
    callback_data: TaskPaginationCallback | None = None,
    state: FSMContext,
    user_id: str,
    get_all_tasks_uc: GetAllTasksUseCase,
    get_tz_uc: GetTimezoneUseCase,
    kbr_builder: KeyboardBuilder,
):
    current_page = 1
    if callback_data:
        current_page = callback_data.page

    user_tz_data = await get_tz_uc.execute(user_id=user_id)
    tasks_with_pagination = await get_all_tasks_uc.execute(
        TaskPaginationRequest(user_id=user_id, page=current_page, page_size=6)
    )
    tasks_formatter = TaskListFormatter(user_tz=user_tz_data.current_timezone)
    formatted_task_list = tasks_formatter.format(tasks_with_pagination)

    if formatted_task_list:
        text = AllTasksMessageFormatter().format(
            formatted_task_list=formatted_task_list
        )
    else:
        text = TEXTS[MsgKey.NO_TASKS]

    extra_buttons = []
    if current_page > 1:
        extra_buttons.append(
            (MsgKey.PREV, TaskPaginationCallback(page=current_page - 1))
        )
    if current_page < tasks_with_pagination.total_pages:
        extra_buttons.append(
            (MsgKey.NEXT, TaskPaginationCallback(page=current_page + 1))
        )

    kbr_builder.conf(row_width=2, extra_buttons=extra_buttons)
    kbr_builder.buttons_text_tuple(
        *[
            (str(idx), TaskCallback(task=el.id, page=current_page))
            for idx, el in enumerate(
                tasks_with_pagination.items, start=tasks_with_pagination.offset + 1
            )
        ]
    )

    await update_main_message(
        state=state,
        event=event,
        text=text,
        reply_markup=kbr_builder.as_markup(),
        create_new=isinstance(event, Message),
    )


@router.callback_query(TaskCallback.filter())
async def task_info(
    callback: CallbackQueryWithMessage,
    callback_data: TaskCallback,
    state: FSMContext,
    user_id: str,
    get_task_uc: GetTaskUseCase,
    get_tz_uc: GetTimezoneUseCase,
    kbr_builder: KeyboardBuilder,
):
    user_tz_data = await get_tz_uc.execute(user_id=user_id)

    task = await get_task_uc.execute(callback_data.task)
    formatted_task = TaskFormatter(user_tz=user_tz_data.current_timezone).format(task)

    kbr_builder.buttons_tuple(
        (MsgKey.EDIT, TaskActionCallback(act=TaskAction.EDIT, id=task.id)),
        (
            MsgKey.MARK_AS_DONE,
            TaskActionCallback(act=TaskAction.MARK_AS_DONE, id=task.id),
        ),
        (MsgKey.DELETE, TaskActionCallback(act=TaskAction.DELETE, id=task.id)),
        (MsgKey.BACK, TaskPaginationCallback(page=callback_data.page)),
    )

    await update_main_message(
        state=state,
        event=callback,
        text=formatted_task,
        reply_markup=kbr_builder.as_markup(),
    )
