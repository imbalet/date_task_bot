from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from date_task_bot.presentation.callbacks import (
    TaskAction,
    TaskActionCallback,
    TaskPaginationCallback,
    TaskUpdateCallback,
    TaskUpdateFields,
)
from date_task_bot.presentation.constants import TEXTS, MsgKey
from date_task_bot.presentation.formatters.messages import UpdatedTaskMessageFormatter
from date_task_bot.presentation.formatters.models import TaskFormatter
from date_task_bot.presentation.states import TaskEditingState
from date_task_bot.presentation.utils import (
    CallbackQueryWithMessage,
    KeyboardBuilder,
    update_main_message,
)
from date_task_bot.repositories.schemas import TaskUpdate
from date_task_bot.use_cases import (
    DeleteTaskUseCase,
    EditTaskUseCase,
    GetTimezoneUseCase,
)

router = Router(name=__name__)


@router.callback_query(TaskActionCallback.filter(F.act == TaskAction.DELETE))
async def delete(
    callback: CallbackQueryWithMessage,
    callback_data: TaskActionCallback,
    state: FSMContext,
    chat_id: str,
    kbr_builder: KeyboardBuilder,
    delete_task_uc: DeleteTaskUseCase,
):
    await delete_task_uc.execute(task_id=callback_data.id, user_id=str(chat_id))

    kbr_builder.button(MsgKey.BACK, TaskPaginationCallback(page=1))

    await update_main_message(
        state=state,
        event=callback,
        text=TEXTS[MsgKey.TASK_DELETED],
        reply_markup=kbr_builder.as_markup(),
    )


@router.callback_query(TaskActionCallback.filter(F.act == TaskAction.EDIT))
async def edit_start(
    callback: CallbackQueryWithMessage,
    callback_data: TaskActionCallback,
    state: FSMContext,
    kbr_builder: KeyboardBuilder,
):

    kbr_builder.button(
        MsgKey.DUE_DATE_FIELD,
        TaskUpdateCallback(id=callback_data.id, f=TaskUpdateFields.DUE_DATE),
    )
    kbr_builder.button(
        MsgKey.TEXT_FIELD,
        TaskUpdateCallback(id=callback_data.id, f=TaskUpdateFields.TEXT),
    )
    kbr_builder.button(MsgKey.BACK, TaskPaginationCallback(page=1))

    await update_main_message(
        state=state,
        event=callback,
        text=TEXTS[MsgKey.CHOOSE_FIELD_TO_UPDATE],
        reply_markup=kbr_builder.as_markup(),
    )


@router.callback_query(TaskUpdateCallback.filter())
async def edit_select_field(
    callback: CallbackQueryWithMessage,
    callback_data: TaskUpdateCallback,
    state: FSMContext,
):
    await state.update_data(task_id=str(callback_data.id))

    # TODO: add mapping
    if callback_data.f == TaskUpdateFields.DUE_DATE:
        await state.set_state(TaskEditingState.AWAIT_DUE_DATE)
        text = TEXTS[MsgKey.SELECT_NEW_DUE_DATE]
    else:
        # callback_data.f == TaskUpdateFields.TEXT
        await state.set_state(TaskEditingState.AWAIT_TEXT)
        text = TEXTS[MsgKey.SELECT_NEW_TEXT]

    await update_main_message(
        state=state,
        event=callback,
        text=text,
    )


@router.message(TaskEditingState())
async def edit_text(
    message: Message,
    state: FSMContext,
    chat_id: str,
    get_tz_uc: GetTimezoneUseCase,
    edit_task_uc: EditTaskUseCase,
):

    if not message.text or not message.text.strip():
        await update_main_message(
            state=state,
            event=message,
            text=TEXTS[MsgKey.TEXT_NOT_FOUND],
        )
        return

    data = await state.get_data()
    if "task_id" not in data:
        await update_main_message(
            state=state,
            event=message,
            text=TEXTS[MsgKey.UNEXPECTED_ERROR],
        )
        return

    current_state = await state.get_state()
    task_id = UUID(data["task_id"])
    user_input = message.text.strip()
    user_tz_data = await get_tz_uc.execute(user_id=chat_id)

    if current_state == TaskEditingState.AWAIT_TEXT.state:
        new_data = TaskUpdate(text=user_input, id=task_id, user_id=chat_id)
        updated_task = await edit_task_uc.execute(data=new_data)
        task_formatter = TaskFormatter(user_tz=user_tz_data.current_timezone)
        formatted_task = task_formatter.format(updated_task)
    else:
        # current_state == TaskEditingState.AWAIT_DUE_DATE.state
        format_string = "%d.%m.%y %H:%M"
        datetime_object = (
            datetime.strptime(user_input, format_string)
            .replace(tzinfo=ZoneInfo(user_tz_data.current_timezone))
            .astimezone(UTC)
        )

        new_data = TaskUpdate(due_date=datetime_object, id=task_id, user_id=chat_id)
        updated_task = await edit_task_uc.execute(data=new_data)
        task_formatter = TaskFormatter(user_tz=user_tz_data.current_timezone)
        formatted_task = task_formatter.format(updated_task)

    answer_text = UpdatedTaskMessageFormatter().format(formatted_task=formatted_task)

    await state.clear()
    await update_main_message(
        state=state,
        event=message,
        text=answer_text,
    )
