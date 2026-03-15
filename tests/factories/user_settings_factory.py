from datetime import timedelta
from typing import NotRequired, TypedDict
from uuid import UUID, uuid4

from date_task_bot.models import (
    DEFAULT_OFFSETS,
    DefaultRemindTimingOrm,
    ReminderOrm,
    UserSettingsOrm,
)
from date_task_bot.repositories.schemas import UserSettingsResponse
from date_task_bot.schemas import (
    DefaultRemindTiming,
    UserSettings,
)

from .factory import AbstractFactory


class UserSettingsFields(TypedDict):
    id: NotRequired[UUID]
    user_id: NotRequired[str]
    timezone: NotRequired[str]
    timings: NotRequired[list[DefaultRemindTiming]]


class UserSettingsFactory(
    AbstractFactory[UserSettingsFields, UserSettings, ReminderOrm]
):
    model_for_validation = UserSettingsResponse

    def make_schema(
        self,
        fields: UserSettingsFields | None = None,
        use_default_offsets: bool = False,
    ) -> UserSettings:
        if not fields:
            fields = {}

        settings_id = fields.get("id", uuid4())
        timings = fields.get("timings")

        if timings:
            timings = [
                i.model_copy(update={"settings_id": settings_id}, deep=True)
                for i in timings
            ]
        elif use_default_offsets:
            timings = [
                make_default_remind_timing(settings_id=settings_id, offset_seconds=i)
                for i in DEFAULT_OFFSETS
            ]

        return UserSettings(
            id=settings_id,
            user_id=fields.get("user_id", ""),
            timezone=fields.get("timezone", "UTC"),
            timings=timings or [],
        )

    def schema_to_orm(self, user_settings: UserSettings) -> UserSettingsOrm:
        orm = UserSettingsOrm(
            timings=list(map(self.make_default_timing_orm, user_settings.timings)),
            user_id=user_settings.user_id,
        )
        orm.id = user_settings.id
        orm.timezone = user_settings.timezone
        return orm

    @staticmethod
    def make_default_timing_orm(
        default_timing: DefaultRemindTiming,
    ) -> DefaultRemindTimingOrm:
        orm = DefaultRemindTimingOrm(
            offset_seconds=default_timing.offset_seconds,
            settings_id=default_timing.settings_id,
        )
        orm.id = default_timing.id
        return orm


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
