from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
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
    UpdateMainMessage,
)
from date_task_bot.repositories.schemas import TaskPaginationRequest
from date_task_bot.schemas import TaskStatus
from date_task_bot.use_cases import (
    GetAllTasksUseCase,
    GetTaskUseCase,
    GetTimezoneUseCase,
)

router = Router(name=__name__)


@router.callback_query(TaskPaginationCallback.filter())
@router.message(Command("tasks", "tasks_all"))
async def all_tasks(
    event: Message | CallbackQueryWithMessage,
    *,
    callback_data: TaskPaginationCallback | None = None,
    state: FSMContext,
    user_id: str,
    get_all_tasks_uc: GetAllTasksUseCase,
    get_tz_uc: GetTimezoneUseCase,
    kbr_builder: KeyboardBuilder,
    update_main_message: UpdateMainMessage,
) -> None:
    await state.set_state(None)

    if isinstance(event, Message):
        status = TaskStatus.PENDING if event.text == "/tasks" else None
        current_page = 1
    elif callback_data:
        status = callback_data.status
        current_page = callback_data.page
    else:
        raise RuntimeError("No message or callback data")

    user_tz_data = await get_tz_uc.execute(user_id=user_id)
    tasks_with_pagination = await get_all_tasks_uc.execute(
        pagination_request=TaskPaginationRequest(
            page=current_page, page_size=6, user_id=user_id, status=status
        )
    )
    tasks_formatter = TaskListFormatter(user_tz=user_tz_data.current_timezone)
    formatted_task_list = tasks_formatter.format(tasks_with_pagination)

    if formatted_task_list:
        text = AllTasksMessageFormatter().format(
            formatted_task_list=formatted_task_list
        )
    else:
        text = TEXTS[MsgKey.NO_TASKS]

    extra_buttons: list[tuple[MsgKey, CallbackData]] = []
    if current_page > 1:
        extra_buttons.append(
            (MsgKey.PREV, TaskPaginationCallback(page=current_page - 1, status=status))
        )
    if current_page < tasks_with_pagination.total_pages:
        extra_buttons.append(
            (MsgKey.NEXT, TaskPaginationCallback(page=current_page + 1, status=status))
        )

    kbr_builder.conf(row_width=2, extra_buttons=extra_buttons)
    kbr_builder.buttons_text_tuple(
        *[
            (str(idx), TaskCallback(task=el.id, page=current_page, status=status))
            for idx, el in enumerate(
                tasks_with_pagination.items, start=tasks_with_pagination.offset + 1
            )
        ],
    )
    if status == TaskStatus.PENDING:
        kbr_builder.row_buttons_tuple(
            (MsgKey.SHOW_ALL, TaskPaginationCallback(page=1, status=None)),
        )
    else:
        kbr_builder.row_buttons_tuple(
            (
                MsgKey.SHOW_PENDING,
                TaskPaginationCallback(page=1, status=TaskStatus.PENDING),
            ),
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
    update_main_message: UpdateMainMessage,
) -> None:
    user_tz_data = await get_tz_uc.execute(user_id=user_id)

    task = await get_task_uc.execute(task_id=callback_data.task, user_id=user_id)
    formatted_task = TaskFormatter(user_tz=user_tz_data.current_timezone).format(task)

    buttons = [
        (MsgKey.EDIT, TaskActionCallback(act=TaskAction.EDIT, id=task.id)),
        (MsgKey.DELETE, TaskActionCallback(act=TaskAction.DELETE, id=task.id)),
        (
            MsgKey.BACK,
            TaskPaginationCallback(
                page=callback_data.page, status=callback_data.status
            ),
        ),
    ]
    if task.status != TaskStatus.DONE:
        buttons.insert(
            1,
            (
                MsgKey.MARK_AS_DONE,
                TaskActionCallback(act=TaskAction.MARK_AS_DONE, id=task.id),
            ),
        )

    kbr_builder.buttons_tuple(*buttons)

    await update_main_message(
        state=state,
        event=callback,
        text=formatted_task,
        reply_markup=kbr_builder.as_markup(),
    )
