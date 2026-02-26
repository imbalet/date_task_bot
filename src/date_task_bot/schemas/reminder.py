from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

from .base_schema import BaseAppSchema


class ReminderStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"


class Reminder(BaseAppSchema):
    id: UUID
    task_id: UUID
    remind_at: datetime
    status: ReminderStatus
    offset_seconds: timedelta
