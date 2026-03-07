from uuid import UUID

from pydantic import Field

from date_task_bot.schemas import DefaultRemindTiming, UserSettings

from .base_schema import RepositoryDTO


class UserSettingsUpdate(RepositoryDTO):
    id: UUID
    timezone: str


class UserSettingsResponse(UserSettings, RepositoryDTO):
    timings: list[DefaultRemindTiming] = Field(default_factory=list)
