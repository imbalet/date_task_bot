from uuid import UUID

from date_task_bot.models import RemindersOrm
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    ReminderResponse,
    TaskResponse,
    UserResponse,
)
from tests.integration.utils import create_entity, get_from_db_by_pk


async def test_create(
    reminder_repo: ReminderRepository,
    task_in_db: TaskResponse,
    async_session_factory,
    reminder_create_schema: ReminderCreate,
):
    res = await reminder_repo.create(reminder_create_schema)

    from_db = ReminderResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, RemindersOrm, res.id)
    )

    assert res.remind_at == reminder_create_schema.remind_at
    assert res.task_id == reminder_create_schema.task_id
    assert res.id == from_db.id


async def test_get(
    reminder_repo: ReminderRepository,
    task_in_db: UserResponse,
    async_session_factory,
    reminder_create_schema: ReminderCreate,
):
    created: RemindersOrm = await create_entity(
        async_session_factory,
        RemindersOrm(**reminder_create_schema.model_dump(mode="python")),
    )

    res = await reminder_repo.get(created.id)  # type: ignore

    assert res
    assert res.task_id == created.task_id


async def test_get_not_exists(reminder_repo: ReminderRepository, fixed_uuid: UUID):
    res = await reminder_repo.get(fixed_uuid)

    assert res is None
