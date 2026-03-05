from datetime import UTC, datetime
from logging import getLogger
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from date_task_bot.exceptions import AppException, EntityEnum
from date_task_bot.models import ReminderOrm, TaskOrm
from date_task_bot.schemas import Task

from .base_repository import BaseRepository
from .schemas import (
    PaginationResponse,
    TaskCreate,
    TaskPaginationRequest,
    TaskResponse,
    TaskUpdate,
)

logger = getLogger(__name__)


class TaskRepository(BaseRepository):
    async def create(self, task: TaskCreate) -> Task:
        async with self.session_factory() as session:
            try:
                new = TaskOrm(
                    user_id=task.user_id,
                    text=task.text,
                    due_date=task.due_date,
                    reminders=[
                        ReminderOrm(
                            remind_at=rem.remind_at, offset_seconds=rem.offset_seconds
                        )
                        for rem in task.reminders
                    ],
                )
                session.add(new)
                await session.flush()
                await session.commit()
                return TaskResponse.model_validate(new)
            except IntegrityError as e:
                await session.rollback()
                logger.exception("Integrity error in TaskRepository", exc_info=True)
                raise AppException(entity=EntityEnum.TASK) from e

    async def get(self, id: UUID, load_reminders: bool = False) -> Task | None:
        async with self.session_factory() as session:
            options = []
            if load_reminders:
                options.append(selectinload(TaskOrm.reminders))

            res = await session.get(TaskOrm, id, options=options)
            if res is None:
                return None
            return TaskResponse.model_validate(res)

    async def get_by_user_id(
        self,
        pagination_request: TaskPaginationRequest,
        load_reminders: bool = False,
    ) -> PaginationResponse[Task]:
        async with self.session_factory() as session:
            options = []
            if load_reminders:
                options.append(selectinload(TaskOrm.reminders))

            total_col = func.count().over()

            stmt = (
                select(TaskOrm, total_col.label("total_items"))
                .options(*options)
                .where(TaskOrm.user_id == pagination_request.user_id)
                .order_by(TaskOrm.created_at.desc())
                .limit(pagination_request.limit)
                .offset(pagination_request.offset)
            )
            status_filter = TaskOrm.status == pagination_request.status
            if pagination_request.status is not None:
                stmt = stmt.where(status_filter)

            res = await session.execute(stmt)
            rows = res.all()

            if not rows:
                return PaginationResponse(
                    page=pagination_request.page,
                    page_size=pagination_request.page_size,
                    total_items=0,
                    items=[],
                )

            tasks: list[Task] = [TaskResponse.model_validate(row[0]) for row in rows]
            total_items = rows[0].total_items

            return PaginationResponse(
                page=pagination_request.page,
                page_size=pagination_request.page_size,
                total_items=total_items,
                items=tasks,
            )

    async def update(self, data: TaskUpdate) -> Task | None:
        async with self.session_factory() as session:
            stmt = (
                update(TaskOrm)
                .values(
                    **data.model_dump(
                        include={"text", "due_date", "status"}, exclude_unset=True
                    ),
                    edited_at=datetime.now(UTC),
                )
                .where(TaskOrm.id == data.id)
                .returning(TaskOrm)
            )
            res = await session.execute(stmt)
            await session.commit()
            result = res.scalar_one_or_none()
            if not result:
                return None

            return TaskResponse.model_validate(result)

    async def delete(self, id: UUID) -> None:
        async with self.session_factory() as session:
            stmt = delete(TaskOrm).where(TaskOrm.id == id)
            await session.execute(stmt)
            await session.commit()
