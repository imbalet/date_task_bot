from uuid import UUID

from date_task_bot.exceptions import EntityEnum, NotFoundException
from date_task_bot.repositories import TaskRepository


class DeleteTaskUseCase:

    def __init__(self, task_repo: TaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(self, task_id: UUID, user_id: str) -> None:
        task = await self.task_repo.get(id=task_id)
        if not task or task.user_id != user_id:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": task_id})

        await self.task_repo.delete(id=task_id)
