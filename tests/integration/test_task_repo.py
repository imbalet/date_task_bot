import asyncio
from copy import deepcopy
from datetime import UTC, datetime
from uuid import UUID

from date_task_bot.models import TaskOrm
from date_task_bot.repositories import TaskRepository
from date_task_bot.repositories.schemas import TaskCreate, TaskResponse, UserResponse
from tests.integration.utils import create_entity, get_from_db_by_pk


async def test_create(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    async_session_factory,
    task_create_schema: TaskCreate,
):
    res = await task_repo.create(task_create_schema)

    from_db = TaskResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, TaskOrm, res.id)
    )

    assert res.text == task_create_schema.text
    assert res.user_id == task_create_schema.user_id
    assert res.created_at <= datetime.now(UTC)
    assert res.id == from_db.id


async def test_get(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
):
    res = await task_repo.get(task_in_db.id)

    assert res
    assert res.text == task_in_db.text
    assert len(res.reminders) == 0


async def test_get_with_reminders(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
):
    res = await task_repo.get(task_in_db.id, load_reminders=True)

    assert res
    assert res.text == task_in_db.text
    assert len(res.reminders) > 0


async def test_get_not_exists(task_repo: TaskRepository, fixed_uuid: UUID):
    res = await task_repo.get(fixed_uuid)

    assert res is None


async def test_get_by_user_id(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    async_session_factory,
    task_orm: TaskOrm,
):
    created1: TaskOrm = await create_entity(async_session_factory, deepcopy(task_orm))
    await asyncio.sleep(1)
    created2: TaskOrm = await create_entity(async_session_factory, deepcopy(task_orm))

    res = await task_repo.get_by_user_id(user_in_db.id)

    assert len(res) == 2
    assert res[0].id == created2.id
    assert res[1].id == created1.id
