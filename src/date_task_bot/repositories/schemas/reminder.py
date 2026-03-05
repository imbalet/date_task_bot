from datetime import timedelta
from uuid import UUID

from date_task_bot.schemas import Reminder

from .base_schema import AwareDatetime, RepositoryDTO


class ReminderCreate(RepositoryDTO):
    task_id: UUID | None = None
    remind_at: AwareDatetime
    offset_seconds: timedelta


class ReminderResponse(Reminder, RepositoryDTO):
    remind_at: AwareDatetime


class DueReminder(RepositoryDTO):
    id: UUID
    task_id: UUID
    remind_at: AwareDatetime
    offset_seconds: timedelta
    user_id: str
    text: str
    due_date: AwareDatetime
    timezone: str
