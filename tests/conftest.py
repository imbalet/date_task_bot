from datetime import UTC, datetime
from uuid import UUID

import pytest

from date_task_bot.repositories.schemas import ReminderCreate, TaskCreate, UserCreate


@pytest.fixture
def fixed_now():
    return datetime(2025, 8, 26, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def fixed_uuid():
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def user_create_schema():
    return UserCreate(id="1234")


@pytest.fixture
def task_create_schema(user_create_schema: UserCreate):
    return TaskCreate(user_id=user_create_schema.id, text="text")


@pytest.fixture
def reminder_create_schema(fixed_now: datetime, fixed_uuid: UUID):
    return ReminderCreate(task_id=fixed_uuid, remind_at=fixed_now)
