from datetime import datetime

from pydantic import Field, field_validator

from date_task_bot.schemas import Reminder, Task

from .base_schema import AwareDatetime, OptionalAwareDatetime, RepositoryDTO
from .reminder import ReminderCreate, ReminderResponse


class TaskCreate(RepositoryDTO):
    user_id: str
    text: str
    due_date: datetime
    reminders: list[ReminderCreate]


class TaskResponse(Task, RepositoryDTO):
    due_date: AwareDatetime
    created_at: AwareDatetime
    edited_at: OptionalAwareDatetime = None
    reminders: list[Reminder] = Field(default_factory=list)

    @field_validator("reminders", mode="before")
    def validate_reminders_as_response(cls, v):
        if not v:
            return []
        return [ReminderResponse.model_validate(item) for item in v]
