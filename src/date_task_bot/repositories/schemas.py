from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from sqlalchemy import inspect

from date_task_bot.schemas import ReminderStatus, TaskStatus


def ensure_timezone(d: datetime | None) -> datetime | None:
    if d is None:
        return None

    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=UTC)
    return d


AwareDatetime = Annotated[datetime, AfterValidator(ensure_timezone)]
OptionalAwareDatetime = Annotated[datetime | None, AfterValidator(ensure_timezone)]


class RepositoryDTO(BaseModel):
    @classmethod
    def model_validate(cls, obj, **kwargs):
        if not hasattr(obj, "__mapper__"):
            return super().model_validate(obj, **kwargs)

        insp = inspect(obj)
        data = {}

        for name in insp.attrs.keys():
            if name not in insp.unloaded:
                try:
                    data[name] = getattr(obj, name)
                except Exception:
                    continue
        return super().model_validate(data, **kwargs)

    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(RepositoryDTO):
    task_id: UUID
    remind_at: AwareDatetime


class ReminderResponse(ReminderCreate):
    id: UUID
    task_id: UUID
    remind_at: AwareDatetime
    status: ReminderStatus


class TaskCreate(RepositoryDTO):
    user_id: str
    text: str


class TaskResponse(TaskCreate):
    id: UUID
    status: TaskStatus
    created_at: AwareDatetime
    edited_at: OptionalAwareDatetime
    reminders: list[ReminderResponse] = Field(default_factory=list)


class UserCreate(RepositoryDTO):
    id: str


class UserResponse(UserCreate):
    created_at: AwareDatetime
    timezone: str
    tasks: list[TaskResponse] = Field(default_factory=list)


class UserUpdate(RepositoryDTO):
    timezone: str
