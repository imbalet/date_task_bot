from datetime import timedelta

from .base_schema import RepositoryDTO


class TaskRemindTimingCreate(RepositoryDTO):
    timing: timedelta
