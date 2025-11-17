from datetime import timedelta
from uuid import UUID, uuid4

from date_task_bot.models import DEFAULT_OFFSETS
from date_task_bot.schemas import DefaultRemindTiming, UserSettings


def make_user_settings(
    *,
    id: UUID | None = None,
    user_id: str | None = None,
    timezone: str = "UTC",
    offsets_seconds: list[DefaultRemindTiming] | None = None,
    use_default_offsets: bool = False,
) -> UserSettings:
    settings_id = id or uuid4()

    if offsets_seconds:
        offsets_seconds = [
            i.model_copy(update={"settings_id": settings_id}, deep=True)
            for i in offsets_seconds
        ]
    elif use_default_offsets:
        offsets_seconds = [
            make_default_remind_timing(settings_id=settings_id, offset_seconds=i)
            for i in DEFAULT_OFFSETS
        ]

    return UserSettings(
        id=settings_id,
        user_id=user_id or "",
        timezone=timezone,
        offsets_seconds=offsets_seconds or [],
    )


def make_default_remind_timing(
    *,
    id: UUID | None = None,
    settings_id: UUID | None = None,
    offset_seconds: timedelta,
) -> DefaultRemindTiming:
    return DefaultRemindTiming(
        id=id or uuid4(),
        settings_id=settings_id or uuid4(),
        offset_seconds=offset_seconds,
    )
