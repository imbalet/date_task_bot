from date_task_bot.exceptions import EntityEnum, NotFoundException
from date_task_bot.repositories import TaskRepository
from date_task_bot.repositories.schemas import TaskUpdate
from date_task_bot.schemas import Task


class EditTaskUseCase:

    def __init__(self, task_repo: TaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(self, data: TaskUpdate) -> Task:

        task = await self.task_repo.get(id=data.id)
        if not task or task.user_id != data.user_id:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        updated_task = await self.task_repo.update(data=data)
        if not updated_task:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        return updated_task
