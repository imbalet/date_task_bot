from datetime import UTC, datetime, timedelta

import pytest

from date_task_bot.repositories.schemas import TaskCreate, TaskResponse
from date_task_bot.schemas import UserSettings
from date_task_bot.use_cases import CreateTaskUseCase
from tests.factories import make_default_remind_timing, make_task


@pytest.fixture
def create_task_uc(task_repo_mock, user_settings_repo_mock):
    return CreateTaskUseCase(
        task_repo=task_repo_mock, user_settings_repo=user_settings_repo_mock
    )


async def test_creating_task(
    user_settings_repo_mock,
    task_repo_mock,
    create_task_uc: CreateTaskUseCase,
    task_create_with_reminders_schema: TaskCreate,
    user_settings_response_schema: UserSettings,
    task_response_schema: TaskResponse,
):
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = task_response_schema

    res = await create_task_uc.execute(
        user_id=task_create_with_reminders_schema.user_id,
        text=task_create_with_reminders_schema.text,
        due_date=task_create_with_reminders_schema.due_date,
    )

    used_reminders = task_repo_mock.create.call_args[0][0].reminders

    assert res == task_response_schema

    assert all(
        used.offset_seconds == actual.offset_seconds
        for used, actual in zip(used_reminders, user_settings_response_schema.timings)
    )
    assert all(
        i.remind_at <= task_create_with_reminders_schema.due_date
        for i in used_reminders
    )
    assert any(
        i.remind_at < task_create_with_reminders_schema.due_date for i in used_reminders
    )


async def test_creating_task_reminders_in_the_past(
    user_settings_repo_mock,
    task_repo_mock,
    create_task_uc: CreateTaskUseCase,
    task_create_with_reminders_schema: TaskCreate,
    user_settings_response_schema: UserSettings,
):
    task = task_create_with_reminders_schema.model_copy(deep=True)
    now = datetime.now(UTC)

    task.due_date = now + timedelta(hours=2)

    user_settings_response_schema.timings = [
        make_default_remind_timing(offset_seconds=timedelta(hours=-1)),
        make_default_remind_timing(offset_seconds=timedelta(hours=-3)),
    ]
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = make_task()

    res = await create_task_uc.execute(
        user_id=task.user_id,
        text=task.text,
        due_date=task.due_date,
    )

    used_reminders = task_repo_mock.create.call_args[0][0].reminders

    assert res

    assert all(
        used.offset_seconds == actual.offset_seconds
        for used, actual in zip(used_reminders, user_settings_response_schema.timings)
    )
    assert all(i.remind_at <= task.due_date for i in used_reminders)
    assert any(i.remind_at < task.due_date for i in used_reminders)
