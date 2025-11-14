from datetime import timedelta
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
