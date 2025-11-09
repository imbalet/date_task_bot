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
    reminders: list[Reminder]

    model_config = ConfigDict(from_attributes=True)
