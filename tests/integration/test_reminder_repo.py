from uuid import UUID

from date_task_bot.models import RemindersOrm
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import (
    ReminderResponse,
    TaskResponse,
    UserResponse,
)
from date_task_bot.repositories.schemas.reminder import ReminderCreateForTask
from tests.integration.utils import get_from_db_by_pk


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
