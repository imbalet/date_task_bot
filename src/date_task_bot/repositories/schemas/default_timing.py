from datetime import timedelta
from uuid import UUID

from .base_schema import RepositoryDTO


class DefaultRemindTimingCreate(RepositoryDTO):
    offset_seconds: timedelta
    settings_id: UUID
