from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReminderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"


class Reminder(BaseModel):
    id: UUID
    task_id: UUID
    remind_at: datetime
    status: ReminderStatus

    model_config = ConfigDict(from_attributes=True)
