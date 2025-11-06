from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict

from date_task_bot.schemas import ReminderStatus


def ensure_timezone(d: datetime | None) -> datetime | None:
    if d is None:
        return None

    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=UTC)
    return d


AwareDatetime = Annotated[datetime, AfterValidator(ensure_timezone)]
OptionalAwareDatetime = Annotated[datetime | None, AfterValidator(ensure_timezone)]


class RepositoryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(RepositoryDTO):
    id: str


class UserResponse(UserCreate):
    created_at: AwareDatetime


class TaskCreate(RepositoryDTO):
    user_id: str
    text: str


class TaskResponse(TaskCreate):
    id: UUID
    created_at: AwareDatetime
    edited_at: OptionalAwareDatetime


class ReminderCreate(RepositoryDTO):
    task_id: UUID
    remind_at: AwareDatetime


class ReminderResponse(ReminderCreate):
    id: UUID
    task_id: UUID
    remind_at: AwareDatetime
    status: ReminderStatus
