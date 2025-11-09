from pydantic import Field

from .base_schema import AwareDatetime, RepositoryDTO
from .task import TaskResponse
from .user_settings import UserSettingsResponse


class UserCreate(RepositoryDTO):
    id: str


class UserResponse(UserCreate):
    created_at: AwareDatetime
    tasks: list[TaskResponse] = Field(default_factory=list)
    settings: UserSettingsResponse | None = Field(default=None)
