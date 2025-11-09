from pydantic import Field

from date_task_bot.schemas import RemindTiming, UserSettings

from .base_schema import RepositoryDTO


class UserSettingsUpdate(RepositoryDTO):
    timezone: str


class UserSettingsResponse(UserSettings, RepositoryDTO):
    timings: list[RemindTiming] = Field(default_factory=list)
