from uuid import UUID

from sqlalchemy.exc import IntegrityError

from date_task_bot.models import RemindersOrm

from .base_repository import BaseRepository
from .exceptions import UNEXPECTED_ERROR, RepositoryException
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
                raise RepositoryException(UNEXPECTED_ERROR)

    async def get(self, id: UUID) -> ReminderResponse | None:
        async with self.session_factory() as session:
            res = await session.get(RemindersOrm, id)
            if res is None:
                return None
            return ReminderResponse.model_validate(res)
