from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from date_task_bot.exceptions import AppException
from date_task_bot.models import ReminderOrm
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    ReminderResponse,
    TaskResponse,
)
from date_task_bot.schemas import ReminderStatus
from tests.factories import ReminderFactory, TaskFactory


async def test_create(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    get_from_db_by_pk,
    reminder_factory: ReminderFactory,
):
    reminder = reminder_factory.make_schema(
        {"task_id": task_without_reminders_in_db.id}
    )

    res = await reminder_repo.create(reminder=ReminderCreate.model_validate(reminder))
    from_db = await get_from_db_by_pk(ReminderOrm, res.id, ReminderResponse)

    assert res.remind_at == reminder.remind_at
    assert res.task_id == reminder.task_id
    assert res.id == from_db.id
    assert res.status == ReminderStatus.PENDING


async def test_create_without_task(
    reminder_repo: ReminderRepository,
    get_from_db_by_pk,
    reminder_factory: ReminderFactory,
):
    reminder = reminder_factory.make_schema()

    with pytest.raises(AppException):
        await reminder_repo.create(reminder=ReminderCreate.model_validate(reminder))

    from_db = await get_from_db_by_pk(ReminderOrm, reminder.id)
    assert from_db is None


async def test_get(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.get(id=reminder_in_db.id)

    assert res
    assert res.task_id == reminder_in_db.task_id


async def test_get_not_exists(reminder_repo: ReminderRepository, fixed_uuid: UUID):
    res = await reminder_repo.get(id=fixed_uuid)

    assert res is None


async def test_get_by_task_id(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.get_by_task_id(task_id=reminder_in_db.task_id)

    assert len(res) == 1
    assert res[0].id == reminder_in_db.id


async def test_get_by_task_id_with_other_task(
    create_entity,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    user_id: str,
    reminder_factory: ReminderFactory,
    task_factory: TaskFactory,
):
    task = await task_factory.insert_to_database({"user_id": user_id})
    await reminder_factory.insert_to_database({"task_id": task.id})

    res = await reminder_repo.get_by_task_id(task_id=reminder_in_db.task_id)

    assert len(res) == 1
    assert res[0].id == reminder_in_db.id


async def test_get_by_task_id_task_not_exists(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
):
    res = await reminder_repo.get_by_task_id(task_id=uuid4())

    assert len(res) == 0


@pytest.mark.parametrize("status", [status for status in ReminderStatus])
async def test_set_status(
    status: ReminderStatus,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    get_from_db_by_pk,
):
    res = await reminder_repo.set_status(id=reminder_in_db.id, status=status)
    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)

    assert res
    assert res.status == status
    assert from_db.status == status


async def test_set_status_empty(
    reminder_repo: ReminderRepository,
    get_from_db_by_pk,
):
    reminder_id = uuid4()
    status = ReminderStatus.FAILED

    res = await reminder_repo.set_status(id=reminder_id, status=status)
    from_db = await get_from_db_by_pk(ReminderOrm, reminder_id)

    assert res is None
    assert from_db is None


@pytest.mark.parametrize("status", [status for status in ReminderStatus])
async def test_set_status_with_other_reminders(
    create_entity,
    get_from_db_by_pk,
    user_id: str,
    status: ReminderStatus,
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    reminder_factory: ReminderFactory,
    task_factory: TaskFactory,
):
    task = await task_factory.insert_to_database({"user_id": user_id})
    other_reminder = await reminder_factory.insert_to_database({"task_id": task.id})

    res = await reminder_repo.set_status(id=reminder_in_db.id, status=status)
    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)
    from_db_other = await get_from_db_by_pk(ReminderOrm, other_reminder.id)

    assert res
    assert res.status == status
    assert from_db.status == status
    assert from_db_other.status == other_reminder.status


async def test_reserve(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
    get_from_db_by_pk,
):
    delta = timedelta(hours=-1)
    new_reminder = await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta,
            "offset_seconds": delta,
        },
    )

    res = await reminder_repo.reserve_due_reminders()

    from_db: ReminderOrm = await get_from_db_by_pk(ReminderOrm, new_reminder.id)

    assert len(res) == 1
    assert res[0].remind_at == new_reminder.remind_at

    assert from_db.status == ReminderStatus.PROCESSING


async def test_reserve_multiply(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
    get_from_db_by_filter,
):
    delta1 = timedelta(hours=-1)
    await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta1,
            "offset_seconds": delta1,
        }
    )

    delta2 = timedelta(hours=-2)
    await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta2,
            "offset_seconds": delta2,
        }
    )

    res = await reminder_repo.reserve_due_reminders()

    from_db = await get_from_db_by_filter(ReminderOrm)

    assert len(res) == 2
    assert from_db
    assert all(rem.status == ReminderStatus.PROCESSING for rem in from_db)


async def test_reserve_multiply_limit(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
):
    delta1 = timedelta(hours=-1)
    await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta1,
            "offset_seconds": delta1,
        }
    )

    delta2 = timedelta(hours=-2)
    await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta2,
            "offset_seconds": delta2,
        }
    )

    res = await reminder_repo.reserve_due_reminders(limit=1)

    assert len(res) == 1


async def test_reserve_multiply_with_other_statuses(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
):
    for idx, status in enumerate(
        [
            ReminderStatus.FAILED,
            ReminderStatus.PENDING,
            ReminderStatus.PROCESSING,
            ReminderStatus.SENT,
        ]
    ):
        delta = timedelta(hours=-1 * idx)
        await reminder_factory.insert_to_database(
            {
                "task_id": task_without_reminders_in_db.id,
                "remind_at": datetime.now(UTC) + delta,
                "offset_seconds": delta,
                "status": status,
            }
        )

    res = await reminder_repo.reserve_due_reminders()

    assert len(res) == 1


async def test_reserve_multiply_with_future(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
):

    delta = timedelta(hours=-1)
    reminder = await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta,
            "offset_seconds": delta,
        }
    )

    future_delta = timedelta(hours=1)
    await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + future_delta,
            "offset_seconds": future_delta,
        }
    )

    res = await reminder_repo.reserve_due_reminders()

    assert len(res) == 1
    assert res[0].id == reminder.id


async def test_delete(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    get_from_db_by_pk,
):
    await reminder_repo.delete(id=reminder_in_db.id)

    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)

    assert from_db is None


async def test_delete_empty(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    get_from_db_by_pk,
):
    await reminder_repo.delete(id=uuid4())

    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)

    assert from_db is not None


async def test_delete_by_task_id(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    get_from_db_by_pk,
):
    await reminder_repo.delete_by_task_id(task_id=reminder_in_db.task_id)

    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)

    assert from_db is None


async def test_delete_by_task_id_empty(
    reminder_repo: ReminderRepository,
    reminder_in_db: ReminderResponse,
    get_from_db_by_pk,
):
    await reminder_repo.delete_by_task_id(task_id=uuid4())

    from_db = await get_from_db_by_pk(ReminderOrm, reminder_in_db.id)

    assert from_db is not None


async def test_update_all(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    reminder_factory: ReminderFactory,
):
    reminders_to_update = [
        await reminder_factory.insert_to_database(
            {
                "task_id": task_without_reminders_in_db.id,
                "offset_seconds": timedelta(hours=-i),
            }
        )
        for i in range(2)
    ]
    no_update_reminder = await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "offset_seconds": timedelta(hours=1),
        }
    )

    updated_reminders = []
    for reminder in reminders_to_update:
        reminder.offset_seconds += timedelta(seconds=100)
        updated_reminders.append(reminder)

    await reminder_repo.update_all(reminders=updated_reminders)

    from_db = await reminder_repo.get_by_task_id(
        task_id=task_without_reminders_in_db.id
    )

    for reminder in from_db:
        if reminder.id == no_update_reminder.id:
            assert reminder == no_update_reminder
        else:
            assert reminder in updated_reminders


async def test_update_all_empty(
    reminder_repo: ReminderRepository, get_from_db_by_filter
):

    await reminder_repo.update_all(reminders=[])
    from_db = await get_from_db_by_filter(ReminderOrm)

    assert from_db is not None
    assert len(from_db) == 0


@pytest.mark.parametrize(
    "status",
    [status for status in ReminderStatus if status != ReminderStatus.PROCESSING],
)
async def test_recover_stuck_reminders(
    reminder_repo: ReminderRepository,
    task_without_reminders_in_db: TaskResponse,
    status: ReminderStatus,
    reminder_factory: ReminderFactory,
    get_from_db_by_pk,
):
    delta1 = timedelta(hours=-1)
    reminder1 = await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta1,
            "offset_seconds": delta1,
            "status": status,
        }
    )

    delta2 = timedelta(hours=-2)
    reminder2 = await reminder_factory.insert_to_database(
        {
            "task_id": task_without_reminders_in_db.id,
            "remind_at": datetime.now(UTC) + delta2,
            "offset_seconds": delta2,
            "status": ReminderStatus.PROCESSING,
        }
    )
    assert reminder1.status == status
    assert reminder2.status == ReminderStatus.PROCESSING

    await reminder_repo.recover_stuck_reminders()
    from_db1 = await get_from_db_by_pk(ReminderOrm, reminder1.id)
    from_db2 = await get_from_db_by_pk(ReminderOrm, reminder2.id)

    assert from_db1.status == status
    assert from_db2.status == ReminderStatus.PENDING
