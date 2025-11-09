from uuid import UUID

from date_task_bot.schemas import Reminder

from .base_schema import AwareDatetime, RepositoryDTO


class ReminderCreate(RepositoryDTO):
    task_id: UUID
    remind_at: AwareDatetime


class ReminderResponse(Reminder, RepositoryDTO):
    remind_at: AwareDatetime
