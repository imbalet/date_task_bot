from enum import StrEnum
from uuid import UUID

from aiogram.filters.callback_data import CallbackData

from date_task_bot.schemas import TaskStatus


class BackCallback(CallbackData, prefix="back"):
    pass


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class ConfirmCallback(CallbackData, prefix="confirm"):
    pass


class TaskCallback(CallbackData, prefix="task"):
    task: UUID
    page: int
    status: TaskStatus | None = None


class TaskPaginationCallback(CallbackData, prefix="task_c"):
    page: int
    status: TaskStatus | None = None


class TaskAction(StrEnum):
    DELETE = "delete"
    EDIT = "edit"
    MARK_AS_DONE = "done"


class TaskActionCallback(CallbackData, prefix="task_a"):
    act: TaskAction
    id: UUID


class TaskUpdateFields(StrEnum):
    TEXT = "text"
    DUE_DATE = "d_date"


class TaskUpdateCallback(CallbackData, prefix="task_u"):
    id: UUID
    # field
    f: TaskUpdateFields
