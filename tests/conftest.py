from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from date_task_bot.repositories.schemas import (
    DefaultRemindTimingCreate,
    ReminderCreate,
    ReminderCreateForTask,
    TaskCreate,
    TaskRemindTimingCreate,
    UserCreate,
    UserResponse,
    UserSettingsResponse,
)


@pytest.fixture
def fixed_now():
    return datetime(2025, 8, 26, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def fixed_uuid():
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def user_id():
    return "1234"


@pytest.fixture
def timezone():
    return "UTC"


# User settings


@pytest.fixture
def user_settings_response_schema(fixed_uuid: UUID, user_id: str, timezone: str):
    return UserSettingsResponse(
        id=fixed_uuid, user_id=user_id, timezone=timezone, timings=[]
    )


# User


@pytest.fixture
def user_create_schema(user_id: str):
    return UserCreate(id=user_id)


@pytest.fixture
def user_response_schema(
    user_create_schema: UserCreate,
    fixed_now: datetime,
    user_settings_response_schema: UserSettingsResponse,
):
    return UserResponse(
        id=user_create_schema.id,
        created_at=fixed_now,
        tasks=[],
        settings=user_settings_response_schema,
    )


# Timings


@pytest.fixture
def sample_task_timings():
    return [
        TaskRemindTimingCreate(timing=timedelta(days=-1)),
        TaskRemindTimingCreate(timing=timedelta(hours=-1)),
    ]


@pytest.fixture
def sample_default_timings():
    return [
        DefaultRemindTimingCreate(timing=timedelta(days=-1)),
        DefaultRemindTimingCreate(timing=timedelta(hours=-1)),
    ]


# Task


@pytest.fixture
def task_create_schema(
    user_create_schema: UserCreate,
    fixed_now: datetime,
    sample_task_timings: list[TaskRemindTimingCreate],
):
    return TaskCreate(
        user_id=user_create_schema.id,
        due_date=fixed_now,
        text="text",
        timings=sample_task_timings,
        reminders=[],
    )


# Reminder


@pytest.fixture
def reminder_create_schema(fixed_now: datetime):
    return ReminderCreate(remind_at=fixed_now)


@pytest.fixture
def reminder_create_for_task_schema(fixed_uuid: UUID, fixed_now: datetime):
    return ReminderCreateForTask(task_id=fixed_uuid, remind_at=fixed_now)


@pytest.fixture
def sample_reminders(
    sample_default_timings: list[DefaultRemindTimingCreate], fixed_now
):
    return [
        ReminderCreate(remind_at=fixed_now + sample_default_timings[0].timing),
        ReminderCreate(remind_at=fixed_now + sample_default_timings[1].timing),
    ]
