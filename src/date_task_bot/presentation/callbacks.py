from enum import StrEnum
from uuid import UUID

from aiogram.filters.callback_data import CallbackData


class BackCallback(CallbackData, prefix="back"):
    pass


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class ConfirmCallback(CallbackData, prefix="confirm"):
    pass


class TaskCallback(CallbackData, prefix="task"):
    task: UUID
    page: int


class TaskPaginationCallback(CallbackData, prefix="task_c"):
    page: int


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
