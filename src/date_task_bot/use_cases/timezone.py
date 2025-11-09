from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from date_task_bot.exceptions import NOT_FOUND_MESSAGE, NotFoundException
from date_task_bot.repositories import UserRepository
from date_task_bot.repositories.schemas import UserUpdate


@dataclass
class SetTimezoneUseCaseResult:
    success: bool = True
    current_time: datetime | None = None
    current_timezone: str | None = None


class SetTimezoneUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: str, tz: str) -> SetTimezoneUseCaseResult:
        if tz not in available_timezones():
            return SetTimezoneUseCaseResult(success=False)
        else:
            res = await self.user_repo.update(id=user_id, data=UserUpdate(timezone=tz))
            now = datetime.now(ZoneInfo(tz))
            return SetTimezoneUseCaseResult(
                current_time=now, current_timezone=res.timezone
            )


@dataclass
class GetTimezoneUseCaseResult:
    current_time: datetime
    current_timezone: str


class GetTimezoneUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: str) -> GetTimezoneUseCaseResult:
        user = await self.user_repo.get(id=user_id)
        if not user:
            raise NotFoundException(
                NOT_FOUND_MESSAGE.format(entity=f"User with id={user_id}")
            )
        now = datetime.now(ZoneInfo(user.timezone))
        return GetTimezoneUseCaseResult(
            current_time=now, current_timezone=user.timezone
        )
