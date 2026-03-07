from uuid import UUID

from date_task_bot.repositories import ReminderRepository, TaskRepository
from date_task_bot.schemas import TaskStatus

from .change_status import ChangeTaskStatusUseCase


class MarkAsDoneUseCase:
    def __init__(
        self, *, task_repo: TaskRepository, reminder_repo: ReminderRepository
    ) -> None:
        self.task_repo = task_repo
        self.reminder_repo = reminder_repo

        self.change_status_uc = ChangeTaskStatusUseCase(task_repo=task_repo)

    async def execute(self, *, task_id: UUID, user_id: str) -> None:
        await self.change_status_uc.execute(
            task_id=task_id, user_id=user_id, status=TaskStatus.DONE
        )
        await self.reminder_repo.delete_by_task_id(task_id=task_id)
