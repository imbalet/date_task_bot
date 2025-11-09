from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .reminder import Reminder


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    DONE = "DONE"


class Task(BaseModel):
    id: UUID
    user_id: str
    text: str
    status: TaskStatus
    created_at: datetime
    edited_at: datetime
    reminders: list[Reminder]

    model_config = ConfigDict(from_attributes=True)
