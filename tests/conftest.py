from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from date_task_bot.repositories.schemas import TaskCreate, UserCreate
from date_task_bot.schemas import Task, User, UserSettings
from tests.factories import (
    ReminderFactory,
    TaskFactory,
    UserFactory,
    UserSettingsFactory,
)


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


# factories


@pytest.fixture
def reminder_factory(create_entity) -> ReminderFactory:
    return ReminderFactory(insert_async_func=create_entity)


@pytest.fixture
def task_factory(create_entity) -> TaskFactory:
    return TaskFactory(insert_async_func=create_entity)


@pytest.fixture
def user_factory(create_entity) -> UserFactory:
    return UserFactory(insert_async_func=create_entity)


@pytest.fixture
def user_settings_factory(create_entity) -> UserSettingsFactory:
    return UserSettingsFactory(insert_async_func=create_entity)


# User
@pytest.fixture
def user_create_schema(user_factory) -> UserCreate:
    return UserCreate.model_validate(user_factory.make_schema())


@pytest.fixture
def user_response_schema(user_id: str, user_factory) -> User:
    return user_factory.make_schema({"id": user_id}, use_default_settings=True)


@pytest.fixture
def user_settings_response_schema(user_settings_factory) -> UserSettings:
    return user_settings_factory.make_schema(use_default_offsets=True)


# Task


@pytest.fixture
def task_create_with_reminders_schema(reminder_factory, task_factory) -> TaskCreate:
    reminders = [
        reminder_factory.make_schema({"offset_seconds": timedelta(hours=-i)})
        for i in range(3)
    ]
    return TaskCreate.model_validate(
        task_factory.make_schema(
            {
                "due_date": datetime.now(UTC) + timedelta(days=1),
                "reminders": reminders,
                "prefer_offset": True,
            }
        )
    )


@pytest.fixture
def task_response_schema(user_id: str, task_factory) -> Task:
    return task_factory.make_schema({"user_id": user_id})
