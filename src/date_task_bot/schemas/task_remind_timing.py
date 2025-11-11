from datetime import timedelta
from uuid import UUID

from .base_schema import BaseAppSchema


class TaskRemindTiming(BaseAppSchema):
    id: UUID
    task_id: UUID
    timing: timedelta
