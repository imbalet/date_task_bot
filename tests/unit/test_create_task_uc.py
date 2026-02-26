from datetime import UTC, datetime, timedelta

import pytest

from date_task_bot.exceptions import EntityEnum, ValidationException
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    TaskCreate,
    TaskResponse,
)
from date_task_bot.schemas import DefaultRemindTiming, UserSettings
from date_task_bot.use_cases import CreateTaskUseCase
from tests.factories import make_default_remind_timing


@pytest.fixture
def create_task_uc(task_repo_mock, user_settings_repo_mock):
    return CreateTaskUseCase(
        task_repo=task_repo_mock, user_settings_repo=user_settings_repo_mock
    )


def _check_reminders_match_timings(
    reminders: list[ReminderCreate], timings: list[DefaultRemindTiming]
):
    if len(reminders) != len(timings):
        return False
    return all(
        rem.offset_seconds == tim.offset_seconds for rem, tim in zip(reminders, timings)
    )


def test_create_reminders(create_task_uc: CreateTaskUseCase):
    due_date = datetime.now(UTC) + timedelta(days=1)
    timings = [
        make_default_remind_timing(offset_seconds=timedelta(hours=-1)),
        make_default_remind_timing(offset_seconds=timedelta(hours=-2)),
        make_default_remind_timing(offset_seconds=timedelta(hours=-3)),
    ]

    reminders = create_task_uc.create_reminders(due_date=due_date, timings=timings)

    assert _check_reminders_match_timings(reminders=reminders, timings=timings)


def test_create_reminders_one_reminder_in_the_past(
    create_task_uc: CreateTaskUseCase,
):
    due_date_delta = timedelta(days=1)
    due_date = datetime.now(UTC) + due_date_delta
    future_timings = [
        make_default_remind_timing(offset_seconds=timedelta(hours=-1)),
        make_default_remind_timing(offset_seconds=timedelta(hours=-2)),
    ]
    past_timing = make_default_remind_timing(
        offset_seconds=-(due_date_delta + timedelta(hours=1))
    )

    reminders = create_task_uc.create_reminders(
        due_date=due_date, timings=[past_timing, *future_timings]
    )

    assert len(reminders) == 2
    assert _check_reminders_match_timings(reminders=reminders, timings=future_timings)


def test_create_reminders_all_in_past(create_task_uc: CreateTaskUseCase):
    due_date = datetime.now(UTC)
    timings = [
        make_default_remind_timing(offset_seconds=timedelta(hours=-1)),
        make_default_remind_timing(offset_seconds=timedelta(hours=-2)),
    ]
    reminders = create_task_uc.create_reminders(due_date=due_date, timings=timings)
    assert reminders == []


def test_create_reminders_empty_timings(create_task_uc: CreateTaskUseCase):
    due_date = datetime.now(UTC) + timedelta(days=1)
    reminders = create_task_uc.create_reminders(due_date=due_date, timings=[])
    assert reminders == []


def test_create_reminders_positive_offsets(create_task_uc: CreateTaskUseCase):
    due_date = datetime.now(UTC)
    timings = [
        make_default_remind_timing(offset_seconds=timedelta(hours=1)),
        make_default_remind_timing(offset_seconds=timedelta(hours=2)),
    ]
    reminders = create_task_uc.create_reminders(due_date=due_date, timings=timings)
    assert _check_reminders_match_timings(reminders=reminders, timings=timings)


async def test_creating_task(
    user_settings_repo_mock,
    task_repo_mock,
    create_task_uc: CreateTaskUseCase,
    task_create_with_reminders_schema: TaskCreate,
    user_settings_response_schema: UserSettings,
    task_response_schema: TaskResponse,
):
    now = datetime.now(UTC)
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = task_response_schema
    task_due_date = task_create_with_reminders_schema.due_date

    res = await create_task_uc.execute(
        user_id=task_create_with_reminders_schema.user_id,
        text=task_create_with_reminders_schema.text,
        due_date=task_due_date,
    )

    used_reminders = task_repo_mock.create.call_args[0][0].reminders

    assert res == task_response_schema

    used_reminders = task_repo_mock.create.call_args[0][0].reminders
    for r in used_reminders:
        assert now < r.remind_at <= task_due_date

    expected_offsets = [t.offset_seconds for t in user_settings_response_schema.timings]
    assert all(r.offset_seconds in expected_offsets for r in used_reminders)


async def test_creating_task_in_the_past(
    user_settings_repo_mock,
    task_repo_mock,
    create_task_uc: CreateTaskUseCase,
    task_create_with_reminders_schema: TaskCreate,
    user_settings_response_schema: UserSettings,
    task_response_schema: TaskResponse,
):
    now = datetime.now(UTC)
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = task_response_schema
    task_due_date = now - timedelta(hours=1)

    with pytest.raises(ValidationException) as e:
        await create_task_uc.execute(
            user_id=task_create_with_reminders_schema.user_id,
            text=task_create_with_reminders_schema.text,
            due_date=task_due_date,
        )
    assert e.value.entity == EntityEnum.TASK

    task_repo_mock.create.assert_not_awaited()
