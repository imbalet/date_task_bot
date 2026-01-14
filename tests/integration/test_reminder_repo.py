from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from date_task_bot.models import ReminderOrm
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
        await get_from_db_by_pk(async_session_factory, ReminderOrm, res.id)
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


async def test_get_by_task_id(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.get_by_task_id(reminder_in_db.task_id)

    assert len(res) == 1
    assert res[0].id == reminder_in_db.id


@pytest.mark.parametrize("status", [status for status in ReminderStatus])
async def test_set_status(
    async_session_factory,
    status: ReminderStatus,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.set_status(id=reminder_in_db.id, status=status)
    from_db = await get_from_db_by_pk(
        async_session_factory, ReminderOrm, reminder_in_db.id
    )

    assert res
    assert res.status == status
    assert from_db.status == status


async def test_set_status_empty(
    async_session_factory,
    reminder_repo: ReminderRepository,
):
    reminder_id = uuid4()
    status = ReminderStatus.FAILED

    res = await reminder_repo.set_status(id=reminder_id, status=status)
    from_db = await get_from_db_by_pk(async_session_factory, ReminderOrm, reminder_id)

    assert res is None
    assert from_db is None


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

    from_db: ReminderOrm = await get_from_db_by_pk(
        async_session_factory, ReminderOrm, new_reminder.id
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

    from_db = await get_from_db_by_filter(async_session_factory, ReminderOrm)

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


async def test_delete(
    async_session_factory,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    await reminder_repo.delete(reminder_in_db.id)

    from_db = await get_from_db_by_pk(
        async_session_factory, ReminderOrm, reminder_in_db.id
    )

    assert from_db is None


async def test_delete_by_task_id(
    async_session_factory,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    await reminder_repo.delete_by_task_id(reminder_in_db.task_id)

    from_db = await get_from_db_by_pk(
        async_session_factory, ReminderOrm, reminder_in_db.id
    )

    assert from_db is None


async def test_update_all(
    async_session_factory,
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
):

    reminders_to_update = [
        make_reminder(
            task_id=task_without_reminders_in_db.id, offset_seconds=timedelta(hours=-i)
        )
        for i in range(2)
    ]
    no_update_reminder = make_reminder(
        task_id=task_without_reminders_in_db.id, offset_seconds=timedelta(hours=1)
    )

    saved_reminders = []
    for reminder in [no_update_reminder, *reminders_to_update]:
        orm_reminder = make_reminder_orm(reminder)
        saved = await create_entity(async_session_factory, orm_reminder)
        saved_reminders.append(ReminderResponse.model_validate(saved))

    updated_reminders = []
    for reminder in saved_reminders[1:]:
        reminder.offset_seconds += timedelta(seconds=100)
        updated_reminders.append(reminder)

    await reminder_repo.update_all(reminders=updated_reminders)

    from_db = await reminder_repo.get_by_task_id(task_without_reminders_in_db.id)

    for reminder in from_db:
        if reminder.id == saved_reminders[0].id:
            assert reminder == saved_reminders[0]
        else:
            assert reminder in updated_reminders


async def test_recover_stuck_reminders(
    async_session_factory,
    reminder_repo: ReminderRepository,
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

    r1_db = await create_entity(
        async_session_factory,
        make_reminder_orm(
            reminder1,
            status=ReminderStatus.PENDING,
        ),
    )
    r2_db = await create_entity(
        async_session_factory,
        make_reminder_orm(
            reminder2,
            status=ReminderStatus.PROCESSING,
        ),
    )
    assert r1_db.status == ReminderStatus.PENDING
    assert r2_db.status == ReminderStatus.PROCESSING

    await reminder_repo.recover_stuck_reminders()
    from_db1 = await get_from_db_by_pk(async_session_factory, ReminderOrm, r1_db.id)
    from_db2 = await get_from_db_by_pk(async_session_factory, ReminderOrm, r2_db.id)

    assert from_db1.status == ReminderStatus.PENDING
    assert from_db2.status == ReminderStatus.PENDING
