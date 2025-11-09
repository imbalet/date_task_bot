from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from date_task_bot.models import Base, RemindersOrm, TaskOrm, UserOrm
from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
)
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    ReminderResponse,
    TaskCreate,
    TaskResponse,
    UserCreate,
    UserResponse,
)
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


# Created entities


@pytest.fixture
async def user_in_db(
    async_session_factory, user_create_schema: UserCreate
) -> UserResponse:
    res = await create_entity(async_session_factory, UserOrm(id=user_create_schema.id))
    return UserResponse.model_validate(res)


@pytest.fixture
async def task_in_db(
    async_session_factory,
    user_in_db: UserResponse,
    task_create_schema: TaskCreate,
    fixed_now: datetime,
) -> TaskResponse:
    res = await create_entity(
        async_session_factory,
        TaskOrm(
            user_id=user_in_db.id, text=task_create_schema.text, due_date=fixed_now
        ),
    )
    return TaskResponse.model_validate(res)


@pytest.fixture
async def reminder_in_db(
    async_session_factory,
    task_in_db: TaskResponse,
    reminder_create_schema: ReminderCreate,
) -> ReminderResponse:
    res = await create_entity(
        async_session_factory,
        RemindersOrm(task_id=task_in_db.id, remind_at=reminder_create_schema.remind_at),
    )
    return ReminderResponse.model_validate(res)
