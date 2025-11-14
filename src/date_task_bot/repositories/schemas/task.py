from datetime import datetime

from date_task_bot.schemas import Task

from .base_schema import AwareDatetime, OptionalAwareDatetime, RepositoryDTO
from .reminder import ReminderCreate


class TaskCreate(RepositoryDTO):
    user_id: str
    text: str
    due_date: datetime
    reminders: list[ReminderCreate]


class TaskResponse(Task, RepositoryDTO):
    due_date: AwareDatetime
    created_at: AwareDatetime
    edited_at: OptionalAwareDatetime = None
