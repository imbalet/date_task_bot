from datetime import timedelta

from .base_schema import RepositoryDTO


class DefaultRemindTimingCreate(RepositoryDTO):
    timing: timedelta
