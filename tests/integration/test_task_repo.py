import asyncio
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
    user_in_db: UserResponse,
    async_session_factory,
    task_create_schema: TaskCreate,
):
    created: TaskOrm = await create_entity(
        async_session_factory, TaskOrm(**task_create_schema.model_dump())
    )

    res = await task_repo.get(created.id)  # type: ignore

    assert res
    assert res.text == created.text


async def test_get_not_exists(task_repo: TaskRepository, fixed_uuid: UUID):
    res = await task_repo.get(fixed_uuid)

    assert res is None


async def test_get_by_user_id(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    async_session_factory,
    task_create_schema: TaskCreate,
):
    created1: TaskOrm = await create_entity(
        async_session_factory, TaskOrm(**task_create_schema.model_dump())
    )
    await asyncio.sleep(1)
    created2: TaskOrm = await create_entity(
        async_session_factory, TaskOrm(**task_create_schema.model_dump())
    )

    res = await task_repo.get_by_user_id(user_in_db.id)

    assert len(res) == 2
    assert res[0].id == created2.id
    assert res[1].id == created1.id
