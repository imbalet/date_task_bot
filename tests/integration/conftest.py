from collections.abc import Awaitable, Callable
from datetime import timedelta
from functools import partial
from pathlib import Path
from typing import TypeVar, cast

import pytest
from pydantic import BaseModel
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from date_task_bot.database import get_sessionmaker
from date_task_bot.models import Base
from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
    UserSettingsRepository,
)
from date_task_bot.repositories.schemas import (
    ReminderResponse,
    TaskResponse,
    UserResponse,
)
from tests.factories import (
    ReminderFactory,
    TaskFactory,
    UserFactory,
)
from tests.integration.utils import create_entity as _create_entity
from tests.integration.utils import get_from_db_by_filter as _get_from_db_by_filter
from tests.integration.utils import get_from_db_by_pk as _get_from_db_by_pk

T = TypeVar("T")


class GetFromDbByPkRet[OrmT, SchemaT: BaseModel]:
    __call__: Callable[[type[OrmT], type[SchemaT] | None], Awaitable[OrmT | SchemaT]]


@pytest.fixture
def get_from_db_by_pk(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> GetFromDbByPkRet:
    return partial(_get_from_db_by_pk, async_session_factory)  # type: ignore


@pytest.fixture
def get_from_db_by_filter(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> GetFromDbByPkRet:
    return partial(_get_from_db_by_filter, async_session_factory)  # type: ignore


@pytest.fixture
def create_entity(async_session_factory) -> Callable[[T], Awaitable[T]]:
    return partial(_create_entity, async_session_factory)


@pytest.fixture(autouse=True)
def patch_config(tmp_path: Path):
    from date_task_bot import config

    db_file = tmp_path / "test.db"

    cfg = config.Config(
        BOT_TOKEN="TEST_TOKEN",  # noqa: S106
        SQLITE_DB_PATH=str(db_file),
    )

    config._config_instance = cfg

    yield cfg

    config._config_instance = None


@pytest.fixture
async def async_session_factory():
    engine, async_sessionmaker = await get_sessionmaker()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_sessionmaker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# Repositories


@pytest.fixture
def user_repo(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> UserRepository:
    return UserRepository(async_session_factory)


@pytest.fixture
def task_repo(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> TaskRepository:
    return TaskRepository(async_session_factory)


@pytest.fixture
def reminder_repo(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> ReminderRepository:
    return ReminderRepository(async_session_factory)


@pytest.fixture
def user_settings_repo(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> UserSettingsRepository:
    return UserSettingsRepository(async_session_factory)


# User


@pytest.fixture
async def user_in_db(user_factory: UserFactory, user_id: str) -> UserResponse:
    return cast(
        UserResponse,
        await user_factory.insert_to_database({"id": user_id}, validate=True),
    )


@pytest.fixture
async def task_in_db(
    user_in_db: UserResponse,
    task_factory: TaskFactory,
    reminder_factory: ReminderFactory,
) -> TaskResponse:
    return cast(
        TaskResponse,
        await task_factory.insert_to_database(
            {
                "user_id": user_in_db.id,
                "reminders": [
                    reminder_factory.make_schema(
                        {"offset_seconds": timedelta(hours=-1)}
                    ),
                    reminder_factory.make_schema(
                        {"offset_seconds": timedelta(hours=-2)}
                    ),
                ],
            }
        ),
    )


@pytest.fixture
async def task_without_reminders_in_db(
    user_in_db: UserResponse, task_factory: TaskFactory
) -> TaskResponse:
    return cast(
        TaskResponse,
        await task_factory.insert_to_database({"user_id": user_in_db.id}),
    )


@pytest.fixture
async def reminder_in_db(
    user_in_db: UserResponse,
    task_factory: TaskFactory,
    reminder_factory: ReminderFactory,
) -> ReminderResponse:
    task = await task_factory.insert_to_database({"user_id": user_in_db.id})
    return cast(
        ReminderResponse,
        await reminder_factory.insert_to_database({"task_id": task.id}),
    )
