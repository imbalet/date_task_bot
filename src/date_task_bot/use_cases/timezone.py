from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from date_task_bot.exceptions import EntityEnum, NotFoundException
from date_task_bot.repositories import UserSettingsRepository
from date_task_bot.repositories.schemas import UserSettingsUpdate


@dataclass
class SetTimezoneUseCaseResult:
    success: bool = True
    current_time: datetime | None = None
    current_timezone: str | None = None


class SetTimezoneUseCase:
    def __init__(self, user_settings_repo: UserSettingsRepository) -> None:
        self.user_settings_repo = user_settings_repo

    async def execute(self, user_id: str, tz: str) -> SetTimezoneUseCaseResult:
        if tz not in available_timezones():
            return SetTimezoneUseCaseResult(success=False)
        else:
            res = await self.user_settings_repo.update(
                user_id=user_id, data=UserSettingsUpdate(timezone=tz)
            )
            now = datetime.now(ZoneInfo(tz))
            return SetTimezoneUseCaseResult(
                current_time=now, current_timezone=res.timezone
            )


@dataclass
class GetTimezoneUseCaseResult:
    current_time: datetime
    current_timezone: str


class GetTimezoneUseCase:
    def __init__(self, user_settings_repo: UserSettingsRepository) -> None:
        self.user_settings_repo = user_settings_repo

    async def execute(self, user_id: str) -> GetTimezoneUseCaseResult:
        user = await self.user_settings_repo.get_by_user_id(user_id=user_id)
        if not user:
            raise NotFoundException(entity=EntityEnum.USER, data={"id": user_id})
        now = datetime.now(ZoneInfo(user.timezone))
        return GetTimezoneUseCaseResult(
            current_time=now, current_timezone=user.timezone
        )
