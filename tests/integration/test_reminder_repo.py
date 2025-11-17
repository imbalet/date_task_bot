from datetime import UTC, datetime, timedelta
from uuid import UUID

from date_task_bot.models import RemindersOrm
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    ReminderResponse,
    TaskResponse,
)
from date_task_bot.schemas import ReminderStatus
from tests.factories import (
    make_reminder,
    make_reminder_orm,
)
from tests.integration.utils import (
    create_entity,
    get_from_db_by_filter,
    get_from_db_by_pk,
)


async def test_create(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    async_session_factory,
):
    reminder = make_reminder(task_id=task_without_reminders_in_db.id)

    res = await reminder_repo.create(ReminderCreate.model_validate(reminder))

    from_db = ReminderResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, RemindersOrm, res.id)
    )

    assert res.remind_at == reminder.remind_at
    assert res.task_id == reminder.task_id
    assert res.id == from_db.id


async def test_get(
    reminder_repo: ReminderRepository,
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
):
    delta = timedelta(hours=-1)
    reminder = make_reminder(
        task_id=task_without_reminders_in_db.id,
        remind_at=datetime.now(UTC) + delta,
        offset_seconds=delta,
    )
    new_reminder = ReminderResponse.model_validate(
        await create_entity(async_session_factory, make_reminder_orm(reminder))
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
):
    delta1 = timedelta(hours=-1)
    reminder1 = make_reminder(
        task_id=task_without_reminders_in_db.id,
        remind_at=datetime.now(UTC) + delta1,
        offset_seconds=delta1,
    )

    delta2 = timedelta(hours=-2)
    reminder2 = make_reminder(
        task_id=task_without_reminders_in_db.id,
        remind_at=datetime.now(UTC) + delta2,
        offset_seconds=delta2,
    )

    await create_entity(async_session_factory, make_reminder_orm(reminder1))
    await create_entity(async_session_factory, make_reminder_orm(reminder2))

    res = await reminder_repo.reserve_due_reminders()

    from_db = await get_from_db_by_filter(async_session_factory, RemindersOrm)

    assert len(res) == 2
    assert from_db
    assert all(rem.status == ReminderStatus.PROCESSING for rem in from_db)


async def test_reserve_multiply_limit(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
):
    delta1 = timedelta(hours=-1)
    reminder1 = make_reminder(
        task_id=task_without_reminders_in_db.id,
        remind_at=datetime.now(UTC) + delta1,
        offset_seconds=delta1,
    )

    delta2 = timedelta(hours=-2)
    reminder2 = make_reminder(
        task_id=task_without_reminders_in_db.id,
        remind_at=datetime.now(UTC) + delta2,
        offset_seconds=delta2,
    )

    await create_entity(async_session_factory, make_reminder_orm(reminder1))
    await create_entity(async_session_factory, make_reminder_orm(reminder2))

    res = await reminder_repo.reserve_due_reminders(limit=1)

    assert len(res) == 1


async def test_reserve_multiply_with_other_statuses(
    reminder_repo: ReminderRepository,
    async_session_factory,
    task_without_reminders_in_db: TaskResponse,
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
        delta = timedelta(hours=-1 * idx)
        reminder = make_reminder(
            task_id=task_without_reminders_in_db.id,
            remind_at=datetime.now(UTC) + delta,
            offset_seconds=delta,
            status=status,
        )
        await create_entity(
            async_session_factory, make_reminder_orm(reminder, status=status)
        )

    res = await reminder_repo.reserve_due_reminders()

    assert len(res) == 1
