from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from date_task_bot.models import (
    Base,
    RemindersOrm,
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
from tests.config import get_config
from tests.factories import (
    make_reminder,
    make_reminder_orm,
    make_task,
    make_task_orm,
    make_user,
    make_user_orm,
)
from tests.integration.utils import create_entity


@pytest.fixture
async def async_session_factory():
    engine = create_async_engine(get_config().DB_URL, echo=True, future=True)

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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
    user = make_user(id=user_id)
    return make_user_orm(user)


@pytest.fixture
async def user_in_db(async_session_factory, user_orm: UserOrm) -> UserResponse:
    res = await create_entity(async_session_factory, user_orm)
    return UserResponse.model_validate(res)


# Task


@pytest.fixture
def task_orm(user_id: str) -> TaskOrm:
    reminders = [
        make_reminder(offset_seconds=timedelta(hours=-1)),
        make_reminder(offset_seconds=timedelta(hours=-2)),
    ]
    task = make_task(user_id=user_id, reminders=reminders)
    return make_task_orm(task)


@pytest.fixture
def task_without_reminders_orm(
    user_in_db: UserResponse, task_response_schema: Task
) -> TaskOrm:
    return make_task_orm(task_response_schema)


@pytest.fixture
async def task_in_db(async_session_factory, task_orm: TaskOrm) -> TaskResponse:
    res = await create_entity(async_session_factory, task_orm)
    return TaskResponse.model_validate(res)


@pytest.fixture
async def task_without_reminders_in_db(
    async_session_factory, task_without_reminders_orm: TaskOrm
) -> TaskResponse:
    res = await create_entity(async_session_factory, task_without_reminders_orm)
    return TaskResponse.model_validate(res)


# Reminder


@pytest.fixture
def reminder_orm() -> RemindersOrm:
    reminder = make_reminder()
    return make_reminder_orm(reminder)


@pytest.fixture
async def reminder_in_db(
    async_session_factory,
    reminder_orm: RemindersOrm,
    task_without_reminders_in_db: TaskResponse,
) -> ReminderResponse:
    reminder_orm.task_id = task_without_reminders_in_db.id
    res = await create_entity(async_session_factory, reminder_orm)
    return ReminderResponse.model_validate(res)
