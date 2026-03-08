from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from date_task_bot.repositories.schemas import TaskCreate, UserCreate
from date_task_bot.schemas import Task, User, UserSettings
from tests.factories import make_reminder, make_task, make_user, make_user_settings


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2025, 8, 26, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def fixed_uuid() -> UUID:
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def user_id() -> str:
    return "1234"


@pytest.fixture
def timezone() -> str:
    return "UTC"


# User
@pytest.fixture
def user_create_schema() -> UserCreate:
    return UserCreate.model_validate(make_user())


@pytest.fixture
def user_response_schema(user_id: str) -> User:
    return make_user(id=user_id, use_default_settings=True)


@pytest.fixture
def user_settings_response_schema() -> UserSettings:
    return make_user_settings(use_default_offsets=True)


# Task


@pytest.fixture
def task_create_with_reminders_schema() -> TaskCreate:
    reminders = [make_reminder(offset_seconds=timedelta(hours=-i)) for i in range(3)]
    return TaskCreate.model_validate(
        make_task(
            due_date=datetime.now(UTC) + timedelta(days=1),
            reminders=reminders,
            prefer_offset=True,
        )
    )


@pytest.fixture
def task_response_schema(user_id: str) -> Task:
    return make_task(user_id=user_id)
