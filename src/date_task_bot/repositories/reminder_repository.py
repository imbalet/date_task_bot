from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.exc import IntegrityError

from date_task_bot.exceptions import AppException, EntityEnum
from date_task_bot.models import ReminderOrm, TaskOrm, UserSettingsOrm
from date_task_bot.schemas import Reminder, ReminderStatus

from .base_repository import BaseRepository
from .schemas import DueReminder, ReminderCreate, ReminderResponse


class ReminderRepository(BaseRepository):

    async def create(self, reminder: ReminderCreate) -> Reminder:
        async with self.session_factory() as session:
            try:
                new = ReminderOrm(
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
                raise AppException(entity=EntityEnum.REMINDER)

    async def bulk_create(self, reminders: list[ReminderCreate]) -> list[Reminder]:
        async with self.session_factory() as session:
            res = await session.execute(
                insert(ReminderOrm).returning(ReminderOrm),
                [r.model_dump() for r in reminders],
            )
            result = res.scalars().all()
            await session.commit()
            return [ReminderResponse.model_validate(i) for i in result]

    async def get(self, id: UUID) -> Reminder | None:
        async with self.session_factory() as session:
            res = await session.get(ReminderOrm, id)
            if res is None:
                return None
            return ReminderResponse.model_validate(res)

    async def get_by_task_id(self, task_id: UUID) -> list[Reminder]:
        async with self.session_factory() as session:
            stmt = (
                select(ReminderOrm)
                .where(ReminderOrm.task_id == task_id)
                .order_by(ReminderOrm.remind_at.desc())
            )
            res = await session.execute(stmt)
            result = res.scalars().all()
            return [ReminderResponse.model_validate(i) for i in result]

    async def set_status(self, id: UUID, status: ReminderStatus) -> Reminder | None:
        async with self.session_factory() as session:
            stmt = (
                update(ReminderOrm)
                .where(ReminderOrm.id == id)
                .values(status=status)
                .returning(ReminderOrm)
            )
            res = await session.execute(stmt)
            await session.commit()
            result = res.scalar()
            if not result:
                return None
            return ReminderResponse.model_validate(result)

    async def reserve_due_reminders(self, limit: int = 300) -> list[DueReminder]:
        async with self.session_factory() as session:
            try:
                now = datetime.now(UTC)
                select_stmt = (
                    select(
                        ReminderOrm.id.label("id"),
                        ReminderOrm.remind_at.label("remind_at"),
                        ReminderOrm.offset_seconds.label("offset_seconds"),
                        TaskOrm.user_id.label("user_id"),
                        TaskOrm.text.label("text"),
                        TaskOrm.due_date.label("due_date"),
                        UserSettingsOrm.timezone.label("timezone"),
                    )
                    .join(TaskOrm, TaskOrm.id == ReminderOrm.task_id)
                    .join(UserSettingsOrm, UserSettingsOrm.user_id == TaskOrm.user_id)
                    .where(
                        ReminderOrm.status == ReminderStatus.PENDING,
                        ReminderOrm.remind_at <= now,
                    )
                    .order_by(ReminderOrm.remind_at)
                    .limit(limit)
                )
                select_res = await session.execute(select_stmt)
                result = select_res.all()
                ids = [i.id for i in result]

                await session.execute(text("BEGIN IMMEDIATE"))
                update_stmt = (
                    update(ReminderOrm)
                    .where(ReminderOrm.id.in_(ids))
                    .values(status=ReminderStatus.PROCESSING)
                )
                await session.execute(update_stmt)
                await session.commit()

                return [DueReminder.model_validate(i) for i in result]

            except IntegrityError:
                await session.rollback()
                raise AppException(entity=EntityEnum.REMINDER)

    async def delete(self, id: UUID) -> None:
        async with self.session_factory() as session:
            stmt = delete(ReminderOrm).where(ReminderOrm.id == id)
            await session.execute(stmt)
            await session.commit()

    async def delete_by_task_id(self, task_id: UUID) -> None:
        async with self.session_factory() as session:
            stmt = delete(ReminderOrm).where(ReminderOrm.task_id == task_id)
            await session.execute(stmt)
            await session.commit()

    async def update_all(self, reminders: list[Reminder]) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ReminderOrm),
                [r.model_dump() for r in reminders],
            )
            await session.commit()

    async def recover_stuck_reminders(self) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(ReminderOrm)
                .where(ReminderOrm.status == ReminderStatus.PROCESSING)
                .values(status=ReminderStatus.PENDING)
            )
            await session.commit()
