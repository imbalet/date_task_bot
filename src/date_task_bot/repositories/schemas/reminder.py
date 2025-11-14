from datetime import datetime, timedelta
from uuid import UUID

from date_task_bot.schemas import Reminder

from .base_schema import AwareDatetime, RepositoryDTO


class ReminderCreate(RepositoryDTO):
    remind_at: AwareDatetime
    offset_seconds: timedelta


class ReminderCreateForTask(ReminderCreate):
    task_id: UUID


class ReminderResponse(Reminder, RepositoryDTO):
    remind_at: AwareDatetime


class DueReminder(RepositoryDTO):
    id: UUID
    remind_at: AwareDatetime
    offset_seconds: timedelta
    user_id: str
    text: str
    due_date: datetime
