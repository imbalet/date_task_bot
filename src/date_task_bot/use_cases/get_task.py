from uuid import UUID

from date_task_bot.exceptions import EntityEnum, NotFoundException
from date_task_bot.repositories import (
    TaskRepository,
)
from date_task_bot.schemas import Task


class GetTaskUseCase:

    def __init__(self, task_repo: TaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(self, task_id: UUID) -> Task:
        res = await self.task_repo.get(id=task_id, load_reminders=True)
        if not res:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": task_id})
        return res
