from uuid import UUID

from .base_schema import BaseAppSchema
from .remind_timing import RemindTiming


class UserSettings(BaseAppSchema):
    id: UUID
    user_id: str
    timezone: str
    timings: list[RemindTiming]
