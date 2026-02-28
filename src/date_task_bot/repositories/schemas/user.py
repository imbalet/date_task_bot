from pydantic import Field, field_validator

from date_task_bot.schemas import Task, User, UserSettings

from .base_schema import AwareDatetime, RepositoryDTO
from .task import TaskResponse
from .user_settings import UserSettingsResponse


class UserCreate(RepositoryDTO):
    id: str


class UserResponse(User, RepositoryDTO):
    created_at: AwareDatetime
    tasks: list[Task] = Field(default_factory=list)
    settings: UserSettings | None = Field(default=None)

    @field_validator("tasks", mode="before")
    def validate_task(cls, v) -> list[Task]:
        if not v:
            return []
        return [TaskResponse.model_validate(item) for item in v]

    @field_validator("settings", mode="before")
    def validate_settings(cls, v) -> UserSettings | None:
        if not v:
            return None
        return UserSettingsResponse.model_validate(v)
