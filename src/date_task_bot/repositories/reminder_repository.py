from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import insert, select, text, update
from sqlalchemy.exc import IntegrityError

from date_task_bot.exceptions import UNEXPECTED_ERROR, AppException
from date_task_bot.models import RemindersOrm, TaskOrm, UserSettingsOrm
from date_task_bot.schemas import ReminderStatus

from .base_repository import BaseRepository
from .schemas import DueReminder, ReminderCreateForTask, ReminderResponse


class ReminderRepository(BaseRepository):

    async def create(self, reminder: ReminderCreateForTask) -> ReminderResponse:
        async with self.session_factory() as session:
            try:
                new = RemindersOrm(
                    task_id=reminder.task_id,
                    remind_at=reminder.remind_at,
                    offset_seconds=reminder.offset_seconds,
                )
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return ReminderResponse.model_validate(new)
            except IntegrityError:
                await session.rollback()
                raise AppException(UNEXPECTED_ERROR)

    async def bulk_create(
        self, reminders: list[ReminderCreateForTask]
    ) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            res = await session.execute(
                insert(RemindersOrm).returning(RemindersOrm),
                [r.model_dump() for r in reminders],
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

    async def set_status(
        self, id: UUID, status: ReminderStatus
    ) -> ReminderResponse | None:
        async with self.session_factory() as session:
            stmt = (
                update(RemindersOrm)
                .where(RemindersOrm.id == id)
                .values(status=status)
                .returning(RemindersOrm)
            )
            res = await session.execute(stmt)
            await session.commit()
            result = res.scalar()
            return ReminderResponse.model_validate(result)

    async def reserve_due_reminders(self, limit: int = 300) -> list[DueReminder]:
        async with self.session_factory() as session:
            try:
                now = datetime.now(UTC)
                select_stmt = (
                    select(
                        RemindersOrm.id.label("id"),
                        RemindersOrm.remind_at.label("remind_at"),
                        RemindersOrm.offset_seconds.label("offset_seconds"),
                        TaskOrm.user_id.label("user_id"),
                        TaskOrm.text.label("text"),
                        TaskOrm.due_date.label("due_date"),
                        UserSettingsOrm.timezone.label("timezone"),
                    )
                    .join(TaskOrm, TaskOrm.id == RemindersOrm.task_id)
                    .join(UserSettingsOrm, UserSettingsOrm.user_id == TaskOrm.user_id)
                    .where(
                        RemindersOrm.status == ReminderStatus.PENDING,
                        RemindersOrm.remind_at <= now,
                    )
                    .order_by(RemindersOrm.remind_at)
                    .limit(limit)
                )
                select_res = await session.execute(select_stmt)
                result = select_res.all()
                ids = [i.id for i in result]

                await session.execute(text("BEGIN IMMEDIATE"))
                update_stmt = (
                    update(RemindersOrm)
                    .where(RemindersOrm.id.in_(ids))
                    .values(status=ReminderStatus.PROCESSING)
                )
                await session.execute(update_stmt)
                await session.commit()

                return [DueReminder.model_validate(i) for i in result]

            except IntegrityError:
                await session.rollback()
                raise AppException(UNEXPECTED_ERROR)
