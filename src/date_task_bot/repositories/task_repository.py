from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from date_task_bot.exceptions import UNEXPECTED_ERROR, AppException
from date_task_bot.models import RemindersOrm, TaskOrm, TaskRemindTimingOrm

from .base_repository import BaseRepository
from .schemas import TaskCreate, TaskResponse


class TaskRepository(BaseRepository):

    async def create(self, task: TaskCreate) -> TaskResponse:
        async with self.session_factory() as session:
            try:
                new = TaskOrm(
                    user_id=task.user_id,
                    text=task.text,
                    due_date=task.due_date,
                    timings=[
                        TaskRemindTimingOrm(timing=tim.timing) for tim in task.timings
                    ],
                    reminders=[
                        RemindersOrm(remind_at=rem.remind_at) for rem in task.reminders
                    ],
                )
                session.add(new)
                await session.flush()
                await session.commit()
                return TaskResponse.model_validate(new)
            except IntegrityError:
                await session.rollback()
                raise AppException(UNEXPECTED_ERROR)

    async def get(self, id: UUID, load_reminders: bool = False) -> TaskResponse | None:
        async with self.session_factory() as session:
            options = []
            if load_reminders:
                options.append(selectinload(TaskOrm.reminders))

            res = await session.get(TaskOrm, id, options=options)
            if res is None:
                return None
            return TaskResponse.model_validate(res)

    async def get_by_user_id(
        self, user_id: str, load_reminders: bool = False
    ) -> list[TaskResponse]:
        async with self.session_factory() as session:
            options = []
            if load_reminders:
                options.append(selectinload(TaskOrm.reminders))
            stmt = (
                select(TaskOrm)
                .options(*options)
                .where(TaskOrm.user_id == user_id)
                .order_by(TaskOrm.created_at.desc())
            )
            res = await session.execute(stmt)
            result = res.scalars().all()
            return [TaskResponse.model_validate(i) for i in result]
