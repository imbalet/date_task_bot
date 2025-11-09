from datetime import datetime
from enum import Enum
from uuid import UUID

from .base_schema import BaseAppSchema


class ReminderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"


class Reminder(BaseAppSchema):
    id: UUID
    task_id: UUID
    remind_at: datetime
    status: ReminderStatus
