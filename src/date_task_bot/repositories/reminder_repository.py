from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from date_task_bot.exceptions import UNEXPECTED_ERROR, AppException
from date_task_bot.models import RemindersOrm

from .base_repository import BaseRepository
from .schemas import ReminderCreate, ReminderResponse


class ReminderRepository(BaseRepository):

    async def create(self, reminder: ReminderCreate) -> ReminderResponse:
        async with self.session_factory() as session:
            try:
                new = RemindersOrm(
                    task_id=reminder.task_id, remind_at=reminder.remind_at
                )
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return ReminderResponse.model_validate(new)
            except IntegrityError:
                await session.rollback()
                raise AppException(UNEXPECTED_ERROR)

    async def bulk_create(
        self, reminders: list[ReminderCreate]
    ) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            res = await session.execute(
                insert(RemindersOrm).returning(RemindersOrm),
                [r.model_dump(mode="json") for r in reminders],
            )
            result = res.scalars().all()
            return [ReminderResponse.model_validate(i) for i in result]

    async def get(self, id: UUID) -> ReminderResponse | None:
        async with self.session_factory() as session:
            res = await session.get(RemindersOrm, id)
            if res is None:
                return None
            return ReminderResponse.model_validate(res)

    async def get_by_task_id(self, task_id: str) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            stmt = (
                select(RemindersOrm)
                .where(RemindersOrm.task_id == task_id)
                .order_by(RemindersOrm.remind_at.desc())
            )
            res = await session.execute(stmt)
            result = res.scalars().all()
            return [ReminderResponse.model_validate(i) for i in result]
