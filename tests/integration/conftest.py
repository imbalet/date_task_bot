from collections.abc import Awaitable, Callable
from datetime import timedelta
from functools import partial
from typing import Any, TypeVar

import pytest

from date_task_bot.database import get_sessionmaker
from date_task_bot.models import (
    Base,
    ReminderOrm,
    TaskOrm,
    UserOrm,
)
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
from date_task_bot.schemas.task import Task
from tests.factories import (
    make_reminder,
    make_reminder_orm,
    make_task,
    make_task_orm,
    make_user,
    make_user_orm,
)
from tests.integration.utils import create_entity as _create_entity
from tests.integration.utils import get_from_db_by_pk as _get_from_db_by_pk

T = TypeVar("T")


@pytest.fixture
def get_from_db_by_pk(
    async_session_factory,
) -> Callable[[type[T], Any], Awaitable[T]]:
    return partial(_get_from_db_by_pk, async_session_factory)


@pytest.fixture
def create_entity(async_session_factory) -> Callable[[T], Awaitable[T]]:
    return partial(_create_entity, async_session_factory)


@pytest.fixture(autouse=True)
def patch_config(tmp_path):
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
def user_repo(async_session_factory) -> UserRepository:
    return UserRepository(async_session_factory)


@pytest.fixture
def task_repo(async_session_factory) -> TaskRepository:
    return TaskRepository(async_session_factory)


@pytest.fixture
def reminder_repo(async_session_factory) -> ReminderRepository:
    return ReminderRepository(async_session_factory)


@pytest.fixture
def user_settings_repo(async_session_factory) -> UserSettingsRepository:
    return UserSettingsRepository(async_session_factory)


# Created entities

# User


@pytest.fixture
def user_orm(user_id: str) -> UserOrm:
    user = make_user(id=user_id, use_default_settings=True)
    return make_user_orm(user)


@pytest.fixture
async def user_in_db(create_entity, user_orm: UserOrm) -> UserResponse:
    res = await create_entity(user_orm)
    return UserResponse.model_validate(res)


# Task


@pytest.fixture
def task_orm(user_in_db: UserResponse) -> TaskOrm:
    reminders = [
        make_reminder(offset_seconds=timedelta(hours=-1)),
        make_reminder(offset_seconds=timedelta(hours=-2)),
    ]
    task = make_task(user_id=user_in_db.id, reminders=reminders)
    return make_task_orm(task)


@pytest.fixture
def task_without_reminders_orm(
    user_in_db: UserResponse, task_response_schema: Task
) -> TaskOrm:
    return make_task_orm(task_response_schema)


@pytest.fixture
async def task_in_db(create_entity, task_orm: TaskOrm) -> TaskResponse:
    res = await create_entity(task_orm)
    return TaskResponse.model_validate(res)


@pytest.fixture
async def task_without_reminders_in_db(
    create_entity, task_without_reminders_orm: TaskOrm
) -> TaskResponse:
    res = await create_entity(task_without_reminders_orm)
    return TaskResponse.model_validate(res)


# Reminder


@pytest.fixture
def reminder_orm() -> ReminderOrm:
    reminder = make_reminder()
    return make_reminder_orm(reminder)


@pytest.fixture
async def reminder_in_db(
    create_entity,
    reminder_orm: ReminderOrm,
    task_without_reminders_in_db: TaskResponse,
) -> ReminderResponse:
    reminder_orm.task_id = task_without_reminders_in_db.id
    res = await create_entity(reminder_orm)
    return ReminderResponse.model_validate(res)
