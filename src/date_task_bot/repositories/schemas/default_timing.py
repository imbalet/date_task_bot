from datetime import timedelta
from uuid import UUID

from .base_schema import RepositoryDTO


class DefaultRemindTimingCreate(RepositoryDTO):
    timing: timedelta


class DefaultRemindTimingCreateForSettings(RepositoryDTO):
    settings_id: UUID
