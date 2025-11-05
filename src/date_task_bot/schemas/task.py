from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .reminder import Reminder


class Task(BaseModel):
    id: UUID
    user_id: str
    text: str
    created_at: datetime
    edited_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskWithReminders(Task):
    tasks: list[Reminder]
