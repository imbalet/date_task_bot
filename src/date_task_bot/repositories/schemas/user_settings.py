from pydantic import Field

from date_task_bot.schemas import DefaultRemindTiming, UserSettings

from .base_schema import RepositoryDTO


class UserSettingsUpdate(RepositoryDTO):
    timezone: str


class UserSettingsResponse(UserSettings, RepositoryDTO):
    offsets_seconds: list[DefaultRemindTiming] = Field(default_factory=list)
