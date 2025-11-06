from uuid import UUID

from sqlalchemy.exc import IntegrityError

from date_task_bot.models import TaskOrm

from .base_repository import BaseRepository
from .exceptions import UNEXPECTED_ERROR, RepositoryException
from .schemas import TaskCreate, TaskResponse


class TaskRepository(BaseRepository):

    async def create(self, task: TaskCreate) -> TaskResponse:
        async with self.session_factory() as session:
            try:
                new = TaskOrm(user_id=task.user_id, text=task.text)
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return TaskResponse.model_validate(new)
            except IntegrityError:
                await session.rollback()
                raise RepositoryException(UNEXPECTED_ERROR)

    async def get(self, id: UUID) -> TaskResponse | None:
        async with self.session_factory() as session:
            res = await session.get(TaskOrm, id)
            if res is None:
                return None
            return TaskResponse.model_validate(res)
