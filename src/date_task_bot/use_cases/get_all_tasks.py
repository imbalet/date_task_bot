from date_task_bot.repositories import (
    TaskRepository,
)
from date_task_bot.repositories.schemas import (
    PaginationResponse,
    TaskPaginationRequest,
)
from date_task_bot.schemas import Task


class GetAllTasksUseCase:
    def __init__(self, task_repo: TaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(
        self, pagination_request: TaskPaginationRequest
    ) -> PaginationResponse[Task]:
        return await self.task_repo.get_by_user_id(
            pagination_request=pagination_request
        )
