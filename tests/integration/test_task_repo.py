from datetime import UTC, datetime, timedelta
from uuid import UUID

from date_task_bot.models import TaskOrm
from date_task_bot.repositories import TaskRepository
from date_task_bot.repositories.schemas import (
    TaskCreate,
    TaskPaginationRequest,
    TaskResponse,
    UserResponse,
)
from tests.factories import make_task, make_task_orm
from tests.integration.utils import create_entity, get_from_db_by_pk


async def test_create(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    async_session_factory,
):
    task = make_task(user_id=user_in_db.id)
    res = await task_repo.create(TaskCreate.model_validate(task))

    from_db = TaskResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, TaskOrm, res.id)
    )

    assert res.text == task.text
    assert res.user_id == task.user_id
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
):
    now = datetime.now(UTC)
    task = make_task(user_id=user_in_db.id)
    created1: TaskOrm = await create_entity(
        async_session_factory, make_task_orm(task, created_at=now)
    )
    created2: TaskOrm = await create_entity(
        async_session_factory,
        make_task_orm(task, created_at=now + timedelta(minutes=1)),
    )

    res = await task_repo.get_by_user_id(
        TaskPaginationRequest(user_id=user_in_db.id, page=1, page_size=2)
    )

    assert res.total_items == 2
    assert len(res.items) == 2
    assert res.items[0].id == created2.id
    assert res.items[1].id == created1.id


async def test_get_by_user_id_pagination(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    async_session_factory,
):
    now = datetime.now(UTC)
    task = make_task(user_id=user_in_db.id)
    created1: TaskOrm = await create_entity(
        async_session_factory, make_task_orm(task, created_at=now)
    )
    created2: TaskOrm = await create_entity(
        async_session_factory,
        make_task_orm(task, created_at=now + timedelta(minutes=1)),
    )

    res = await task_repo.get_by_user_id(
        TaskPaginationRequest(user_id=user_in_db.id, page=1, page_size=1)
    )

    assert res.total_items == 2
    assert len(res.items) == 1
    assert res.items[0].id == created2.id

    res = await task_repo.get_by_user_id(
        TaskPaginationRequest(user_id=user_in_db.id, page=2, page_size=1)
    )

    assert res.total_items == 2
    assert len(res.items) == 1
    assert res.items[0].id == created1.id


async def test_get_by_user_id_empty(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
):
    res = await task_repo.get_by_user_id(
        TaskPaginationRequest(user_id=user_in_db.id, page=1, page_size=1)
    )

    assert res.total_items == 0
    assert len(res.items) == 0
