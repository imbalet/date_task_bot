from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from date_task_bot.repositories.schemas import (
    DefaultRemindTimingCreate,
    ReminderCreate,
    ReminderCreateForTask,
    TaskCreate,
    TaskResponse,
    UserCreate,
    UserResponse,
    UserSettingsResponse,
)
from date_task_bot.schemas import DefaultRemindTiming, TaskStatus


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
def user_settings_empty_response_schema(fixed_uuid: UUID, user_id: str, timezone: str):
    return UserSettingsResponse(
        id=fixed_uuid, user_id=user_id, timezone=timezone, offsets_seconds=[]
    )


@pytest.fixture
def user_settings_response_schema(
    fixed_uuid: UUID,
    user_id: str,
    timezone: str,
    sample_default_timings_response: list[DefaultRemindTiming],
):
    return UserSettingsResponse(
        id=fixed_uuid,
        user_id=user_id,
        timezone=timezone,
        offsets_seconds=sample_default_timings_response,
    )


# User


@pytest.fixture
def user_create_schema(user_id: str):
    return UserCreate(id=user_id)


@pytest.fixture
def user_response_schema(
    user_create_schema: UserCreate,
    fixed_now: datetime,
    user_settings_empty_response_schema: UserSettingsResponse,
):
    return UserResponse(
        id=user_create_schema.id,
        created_at=fixed_now,
        tasks=[],
        settings=user_settings_empty_response_schema,
    )


# Timings


@pytest.fixture
def sample_default_timings_create():
    return [
        DefaultRemindTimingCreate(offset_seconds=timedelta(days=-1)),
        DefaultRemindTimingCreate(offset_seconds=timedelta(hours=-1)),
    ]


@pytest.fixture
def sample_default_timings_response(sample_default_timings_create, fixed_uuid):
    return [
        DefaultRemindTiming(
            id=uuid4(),
            settings_id=fixed_uuid,
            offset_seconds=i.offset_seconds,
        )
        for i in sample_default_timings_create
    ]


# Task


@pytest.fixture
def task_create_schema(user_create_schema: UserCreate, fixed_now: datetime):
    return TaskCreate(
        user_id=user_create_schema.id,
        due_date=fixed_now,
        text="text",
        reminders=[],
    )


@pytest.fixture
def task_response_schema(
    task_create_schema: TaskCreate, fixed_uuid: UUID, user_id: str, fixed_now: datetime
):
    return TaskResponse(
        id=fixed_uuid,
        user_id=user_id,
        text=task_create_schema.text,
        due_date=task_create_schema.due_date,
        status=TaskStatus.PENDING,
        created_at=fixed_now,
        edited_at=None,
        reminders=[],
    )


# Reminder


@pytest.fixture
def default_offset_seconds():
    return timedelta(hours=-3)


@pytest.fixture
def reminder_create_schema(fixed_now: datetime, default_offset_seconds: timedelta):
    return ReminderCreate(remind_at=fixed_now, offset_seconds=default_offset_seconds)


@pytest.fixture
def reminder_create_for_task_schema(
    fixed_uuid: UUID, fixed_now: datetime, default_offset_seconds: timedelta
):
    return ReminderCreateForTask(
        task_id=fixed_uuid, remind_at=fixed_now, offset_seconds=default_offset_seconds
    )


@pytest.fixture
def sample_reminders(
    sample_default_timings_create: list[DefaultRemindTimingCreate], fixed_now: datetime
):
    return [
        ReminderCreate(
            remind_at=fixed_now + sample_default_timings_create[0].offset_seconds,
            offset_seconds=sample_default_timings_create[0].offset_seconds,
        ),
        ReminderCreate(
            remind_at=fixed_now + sample_default_timings_create[1].offset_seconds,
            offset_seconds=sample_default_timings_create[1].offset_seconds,
        ),
    ]
