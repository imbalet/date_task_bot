from datetime import timedelta
from uuid import UUID

from .base_schema import BaseAppSchema


class DefaultRemindTiming(BaseAppSchema):
    id: UUID
    settings_id: UUID
    timing: timedelta
