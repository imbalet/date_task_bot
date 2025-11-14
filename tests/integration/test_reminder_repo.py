from copy import deepcopy
from datetime import UTC, datetime, timedelta
from uuid import UUID

from date_task_bot.models import RemindersOrm
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import (
    ReminderResponse,
    TaskResponse,
    UserResponse,
)
from date_task_bot.repositories.schemas.reminder import ReminderCreateForTask
from date_task_bot.schemas import ReminderStatus
from tests.integration.utils import create_entity, get_from_db_by_pk


async def test_create(
    reminder_repo: ReminderRepository,
    task_in_db: TaskResponse,
    async_session_factory,
    reminder_create_for_task_schema: ReminderCreateForTask,
):
    res = await reminder_repo.create(reminder_create_for_task_schema)

    from_db = ReminderResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, RemindersOrm, res.id)
    )

    assert res.remind_at == reminder_create_for_task_schema.remind_at
    assert res.task_id == reminder_create_for_task_schema.task_id
    assert res.id == from_db.id


async def test_get(
    reminder_repo: ReminderRepository,
    task_in_db: UserResponse,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.get(reminder_in_db.id)

    assert res
    assert res.task_id == reminder_in_db.task_id


async def test_get_not_exists(reminder_repo: ReminderRepository, fixed_uuid: UUID):
    res = await reminder_repo.get(fixed_uuid)

    assert res is None


async def test_reserve(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
    reminder_orm: RemindersOrm,
):
    reminder_orm.task_id = task_without_reminders_in_db.id
    reminder_orm.remind_at = datetime.now(UTC) - timedelta(hours=1)
    reminder_orm.offset_seconds = timedelta(hours=1)

    new_reminder = ReminderResponse.model_validate(
        await create_entity(async_session_factory, reminder_orm)
    )

    res = await reminder_repo.reserve_due_reminders()

    from_db: RemindersOrm = await get_from_db_by_pk(
        async_session_factory, RemindersOrm, new_reminder.id
    )

    assert len(res) == 1
    assert res[0].remind_at == new_reminder.remind_at

    assert from_db.status == ReminderStatus.PROCESSING


async def test_reserve_multiply(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
    reminder_orm: RemindersOrm,
):
    reminder_orm.task_id = task_without_reminders_in_db.id
    reminder_orm.remind_at = datetime.now(UTC) - timedelta(hours=1)
    reminder_orm.offset_seconds = timedelta(hours=1)

    reminder_orm1 = deepcopy(reminder_orm)
    reminder_orm1.remind_at = datetime.now(UTC) - timedelta(hours=2)
    reminder_orm1.offset_seconds = timedelta(hours=2)

    await create_entity(async_session_factory, reminder_orm)
    await create_entity(async_session_factory, reminder_orm1)

    res = await reminder_repo.reserve_due_reminders()

    assert len(res) == 2


async def test_reserve_multiply_limit(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
    reminder_orm: RemindersOrm,
):
    reminder_orm.task_id = task_without_reminders_in_db.id
    reminder_orm.remind_at = datetime.now(UTC) - timedelta(hours=1)
    reminder_orm.offset_seconds = timedelta(hours=1)

    reminder_orm1 = deepcopy(reminder_orm)
    reminder_orm1.remind_at = datetime.now(UTC) - timedelta(hours=2)
    reminder_orm1.offset_seconds = timedelta(hours=2)

    await create_entity(async_session_factory, reminder_orm)
    await create_entity(async_session_factory, reminder_orm1)

    res = await reminder_repo.reserve_due_reminders(limit=1)

    assert len(res) == 1


async def test_reserve_multiply_with_other_statuses(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
    reminder_orm: RemindersOrm,
):
    # TODO: add factory
    for idx, status in enumerate(
        [
            ReminderStatus.FAILED,
            ReminderStatus.PENDING,
            ReminderStatus.PROCESSING,
            ReminderStatus.SENT,
        ]
    ):
        orm_model = deepcopy(reminder_orm)
        orm_model.task_id = task_without_reminders_in_db.id
        orm_model.remind_at = datetime.now(UTC) - timedelta(hours=idx)
        orm_model.offset_seconds = timedelta(hours=idx)
        orm_model.status = status
        await create_entity(async_session_factory, orm_model)

    res = await reminder_repo.reserve_due_reminders()

    assert len(res) == 1
