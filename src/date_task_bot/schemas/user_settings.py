from uuid import UUID

from .base_schema import BaseAppSchema
from .default_remind_timing import DefaultRemindTiming


class UserSettings(BaseAppSchema):
    id: UUID
    user_id: str
    timezone: str
    offsets_seconds: list[DefaultRemindTiming]
