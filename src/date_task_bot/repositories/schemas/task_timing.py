from datetime import timedelta
from uuid import UUID

from .base_schema import RepositoryDTO


class TaskRemindTimingCreate(RepositoryDTO):
    timing: timedelta


class TaskRemindTimingCreateForTask(RepositoryDTO):
    task_id: UUID
