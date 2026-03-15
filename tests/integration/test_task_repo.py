from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from date_task_bot.models import TaskOrm
from date_task_bot.repositories import TaskRepository
from date_task_bot.repositories.schemas import (
    TaskCreate,
    TaskPaginationRequest,
    TaskResponse,
    TaskUpdate,
    UserResponse,
)
from date_task_bot.schemas import TaskStatus
from tests.factories import TaskFactory, UserFactory


async def test_create(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    task_factory: TaskFactory,
    get_from_db_by_pk,
):
    task = task_factory.make_schema({"user_id": user_in_db.id})
    res = await task_repo.create(task=TaskCreate.model_validate(task))

    from_db = TaskResponse.model_validate(await get_from_db_by_pk(TaskOrm, res.id))

    assert res.text == task.text
    assert res.user_id == task.user_id
    assert res.created_at <= datetime.now(UTC)
    assert res.id == from_db.id


async def test_get(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
):
    res = await task_repo.get(id=task_in_db.id)

    assert res
    assert res.text == task_in_db.text
    assert len(res.reminders) == 0


async def test_get_with_reminders(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
):
    res = await task_repo.get(id=task_in_db.id, load_reminders=True)

    assert res
    assert res.text == task_in_db.text
    assert len(res.reminders) > 0


async def test_get_not_exists(task_repo: TaskRepository, fixed_uuid: UUID):
    res = await task_repo.get(id=fixed_uuid)

    assert res is None


async def test_get_by_user_id(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    task_factory: TaskFactory,
):
    now = datetime.now(UTC)

    # for correct sorting
    created1 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "created_at": now}
    )
    created2 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "created_at": now + timedelta(minutes=1)}
    )

    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=2
        )
    )

    assert res.total_items == 2
    assert len(res.items) == 2
    assert res.items[0].id == created2.id
    assert res.items[1].id == created1.id


async def test_get_by_user_id_with_status(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    task_factory: TaskFactory,
):
    now = datetime.now(UTC)

    # for correct sorting
    created1 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "status": TaskStatus.DONE, "created_at": now}
    )
    created2 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "created_at": now + timedelta(minutes=1)}
    )

    res_done = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=2, status=TaskStatus.DONE
        )
    )
    res_pending = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=2, status=TaskStatus.PENDING
        )
    )

    assert res_done.total_items == 1
    assert len(res_done.items) == 1
    assert res_done.items[0].id == created1.id

    assert res_pending.total_items == 1
    assert len(res_pending.items) == 1
    assert res_pending.items[0].id == created2.id


@pytest.mark.parametrize("status", [TaskStatus.DONE, TaskStatus.PENDING])
async def test_get_by_user_id_with_status_multiple(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    status: TaskStatus,
    task_factory: TaskFactory,
):
    now = datetime.now(UTC)

    # for correct sorting
    created1 = await task_factory.insert_to_database(
        {
            "user_id": user_in_db.id,
            "status": status,
            "created_at": now,
        }
    )
    created2 = await task_factory.insert_to_database(
        {
            "user_id": user_in_db.id,
            "status": status,
            "created_at": now + timedelta(minutes=1),
        }
    )

    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=2, status=status
        )
    )

    assert res.total_items == 2
    assert len(res.items) == 2
    assert res.items[0].id == created2.id
    assert res.items[1].id == created1.id


@pytest.mark.parametrize("status1", [TaskStatus.DONE, TaskStatus.PENDING])
@pytest.mark.parametrize("status2", [TaskStatus.DONE, TaskStatus.PENDING])
async def test_get_by_user_id_with_status_with_other_user_different_statuses(
    task_repo: TaskRepository,
    status1: TaskStatus,
    status2: TaskStatus,
    task_factory: TaskFactory,
    user_factory: UserFactory,
):

    user1 = await user_factory.insert_to_database({"id": "0"})
    user2 = await user_factory.insert_to_database({"id": "1"})

    now = datetime.now(UTC)
    created1 = await task_factory.insert_to_database(
        {
            "user_id": user1.id,
            "status": status1,
            "created_at": now,
        }
    )
    await task_factory.insert_to_database(
        {
            "user_id": user2.id,
            "status": status2,
            "created_at": now,
        }
    )

    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user1.id, page=1, page_size=2, status=status1
        )
    )

    assert res.total_items == 1
    assert len(res.items) == 1
    assert res.items[0].id == created1.id


async def test_get_by_user_id_with_pagination(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    task_factory: TaskFactory,
):
    now = datetime.now(UTC)
    created1 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "created_at": now}
    )
    created2 = await task_factory.insert_to_database(
        {"user_id": user_in_db.id, "created_at": now + timedelta(minutes=1)}
    )

    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=1
        )
    )

    assert res.total_items == 2
    assert len(res.items) == 1
    assert res.items[0].id == created2.id

    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=2, page_size=1
        )
    )

    assert res.total_items == 2
    assert len(res.items) == 1
    assert res.items[0].id == created1.id


async def test_get_by_user_id_empty(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
):
    res = await task_repo.get_with_pagination(
        pagination_request=TaskPaginationRequest(
            user_id=user_in_db.id, page=1, page_size=1
        )
    )

    assert res.total_items == 0
    assert len(res.items) == 0


async def test_update(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
    get_from_db_by_pk,
):
    data = TaskUpdate(id=task_in_db.id, text="new text")

    res = await task_repo.update(data=data)

    from_db = await get_from_db_by_pk(TaskOrm, task_in_db.id, TaskResponse)

    assert res == from_db
    assert from_db.text == data.text
    assert from_db.due_date == task_in_db.due_date
    assert from_db.edited_at


async def test_update_empty_with_user(
    task_repo: TaskRepository,
    user_in_db: UserResponse,
    get_from_db_by_pk,
):
    task_id = uuid4()
    data = TaskUpdate(id=task_id, text="new text")

    res = await task_repo.update(data=data)

    from_db = await get_from_db_by_pk(TaskOrm, task_id)

    assert res is None
    assert from_db is None


async def test_delete(
    task_repo: TaskRepository,
    task_in_db: TaskResponse,
    get_from_db_by_pk,
):
    await task_repo.delete(id=task_in_db.id)

    from_db = await get_from_db_by_pk(TaskOrm, task_in_db.id)
    assert from_db is None
