from datetime import UTC, datetime

import pytest

from date_task_bot.models import UserOrm
from date_task_bot.repositories import UserRepository
from date_task_bot.exceptions import AlreadyExistsException
from date_task_bot.repositories.schemas import UserCreate, UserResponse
from tests.integration.utils import create_entity, get_from_db_by_pk


async def test_create(
    user_repo: UserRepository, async_session_factory, user_create_schema: UserCreate
):
    res = await user_repo.create(user_create_schema)

    from_db = UserResponse.model_validate(
        await get_from_db_by_pk(async_session_factory, UserOrm, user_create_schema.id)
    )

    assert res.id == user_create_schema.id
    assert res.created_at <= datetime.now(UTC)
    assert res.id == from_db.id


async def test_create_already_exists(
    user_repo: UserRepository, async_session_factory, user_create_schema: UserCreate
):
    await create_entity(async_session_factory, UserOrm(id=user_create_schema.id))
    with pytest.raises(AlreadyExistsException):
        await user_repo.create(user_create_schema)


async def test_get(
    user_repo: UserRepository, async_session_factory, user_create_schema: UserCreate
):
    await create_entity(async_session_factory, UserOrm(id=user_create_schema.id))

    res = await user_repo.get(user_create_schema.id)

    assert res
    assert res.id == user_create_schema.id


async def test_get_not_exists(
    user_repo: UserRepository, async_session_factory, user_create_schema: UserCreate
):
    res = await user_repo.get(user_create_schema.id)

    assert res is None
