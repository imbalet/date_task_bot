from datetime import timedelta
from uuid import UUID

from .base_schema import BaseAppSchema


class RemindTiming(BaseAppSchema):
    id: str
    settings_id: UUID
    timing: timedelta
