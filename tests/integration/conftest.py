from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from date_task_bot.models import (
    Base,
    RemindersOrm,
    TaskOrm,
    TaskRemindTimingOrm,
    UserOrm,
)
from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
    UserSettingsRepository,
)
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    ReminderResponse,
    TaskCreate,
    TaskResponse,
    UserCreate,
    UserResponse,
)
from date_task_bot.repositories.schemas.task_timing import TaskRemindTimingCreate
from tests.config import get_config
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
def user_orm(user_create_schema: UserCreate):
    return UserOrm(id=user_create_schema.id)


@pytest.fixture
async def user_in_db(async_session_factory, user_orm: UserOrm) -> UserResponse:
    res = await create_entity(async_session_factory, user_orm)
    return UserResponse.model_validate(res)


# Task


@pytest.fixture
def task_orm(
    user_in_db: UserResponse,
    task_create_schema: TaskCreate,
    fixed_now: datetime,
    sample_task_timings: list[TaskRemindTimingCreate],
    sample_reminders: list[ReminderCreate],
):
    return TaskOrm(
        user_id=user_in_db.id,
        text=task_create_schema.text,
        due_date=fixed_now,
        timings=[TaskRemindTimingOrm(timing=t.timing) for t in sample_task_timings],
        reminders=[RemindersOrm(remind_at=r.remind_at) for r in sample_reminders],
    )


@pytest.fixture
async def task_in_db(async_session_factory, task_orm: TaskOrm) -> TaskResponse:
    res = await create_entity(async_session_factory, task_orm)
    return TaskResponse.model_validate(res)


# Reminder


@pytest.fixture
def reminder_orm(task_in_db: TaskResponse, reminder_create_schema: ReminderCreate):
    return RemindersOrm(
        task_id=task_in_db.id, remind_at=reminder_create_schema.remind_at
    )


@pytest.fixture
async def reminder_in_db(
    async_session_factory, reminder_orm: RemindersOrm
) -> ReminderResponse:
    res = await create_entity(async_session_factory, reminder_orm)
    return ReminderResponse.model_validate(res)
