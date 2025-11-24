from datetime import UTC, datetime

import pytest

from date_task_bot.exceptions import AlreadyExistsException
from date_task_bot.models import UserOrm, UserSettingsOrm
from date_task_bot.repositories import UserRepository
from date_task_bot.repositories.schemas import UserCreate, UserResponse
from date_task_bot.repositories.schemas.task import TaskResponse
from tests.factories import make_user, make_user_orm
from tests.integration.utils import (
    create_entity,
    get_from_db_by_filter,
    get_from_db_by_pk,
)


async def test_create(
    user_repo: UserRepository, async_session_factory, user_create_schema
):
    res = await user_repo.create(user_create_schema)

    from_db = UserResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, UserOrm, user_create_schema.id)
    )
    settings = get_from_db_by_filter(
        async_session_factory,
        UserSettingsOrm,
        scalar=True,
        filters=[UserSettingsOrm.user_id == res.id],
    )

    assert settings is not None
    assert res.id == user_create_schema.id
    assert res.created_at <= datetime.now(UTC)
    assert res.id == from_db.id


async def test_create_already_exists(user_repo: UserRepository, async_session_factory):
    user = make_user()
    await create_entity(async_session_factory, make_user_orm(user))
    with pytest.raises(AlreadyExistsException):
        await user_repo.create(UserCreate.model_validate(user))


async def test_get(
    user_repo: UserRepository,
    user_in_db: UserResponse,
    task_in_db: TaskResponse,
):
    res = await user_repo.get(user_in_db.id)

    assert res
    assert res.id == user_in_db.id

    assert len(res.tasks) == 0
    assert res.settings is None


async def test_get_load_settings(
    user_repo: UserRepository,
    user_in_db: UserResponse,
):
    res = await user_repo.get(user_in_db.id, load_settings=True)

    assert res
    assert res.id == user_in_db.id

    assert res.settings is not None


async def test_get_load_tasks(
    user_repo: UserRepository,
    user_in_db: UserResponse,
    task_in_db: TaskResponse,
):
    res = await user_repo.get(user_in_db.id, load_tasks=True)

    assert res
    assert res.id == user_in_db.id

    assert len(res.tasks) == 1
    assert res.tasks[0] == task_in_db
    assert res.settings is None
    assert len(res.tasks[0].reminders) == 0


async def test_get_load_tasks_reminders(
    user_repo: UserRepository,
    user_in_db: UserResponse,
    task_in_db: TaskResponse,
):
    res = await user_repo.get(user_in_db.id, load_tasks=True, load_reminders=True)

    assert res
    assert res.id == user_in_db.id

    assert len(res.tasks[0].reminders) > 0


async def test_get_not_exists(user_repo: UserRepository):
    res = await user_repo.get("non existing id")

    assert res is None
