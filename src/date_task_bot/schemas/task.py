from datetime import datetime
from enum import StrEnum
from uuid import UUID

from .base_schema import BaseAppSchema
from .reminder import Reminder


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    DONE = "DONE"


class Task(BaseAppSchema):
    id: UUID
    user_id: str
    text: str
    due_date: datetime
    status: TaskStatus
    created_at: datetime
    edited_at: datetime | None
    reminders: list[Reminder]
