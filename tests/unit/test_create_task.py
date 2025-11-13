import pytest

from date_task_bot.repositories.schemas.task import TaskCreate, TaskResponse
from date_task_bot.repositories.schemas.user_settings import UserSettingsResponse
from date_task_bot.use_cases import CreateTaskUseCase


@pytest.fixture
def create_task_uc(task_repo_mock, user_settings_repo_mock):
    return CreateTaskUseCase(
        task_repo=task_repo_mock, user_settings_repo=user_settings_repo_mock
    )


async def test_creating_task(
    user_settings_repo_mock,
    task_repo_mock,
    create_task_uc: CreateTaskUseCase,
    task_create_schema: TaskCreate,
    user_settings_response_schema: UserSettingsResponse,
    task_response_schema: TaskResponse,
):
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = task_response_schema

    res = await create_task_uc.execute(
        user_id=task_create_schema.user_id,
        text=task_create_schema.text,
        due_date=task_create_schema.due_date,
    )

    used_timings = task_repo_mock.create.call_args[0][0].timings
    used_reminders = task_repo_mock.create.call_args[0][0].reminders

    assert res.task == task_response_schema

    assert all(
        used.timing == actual.timing
        for used, actual in zip(used_timings, user_settings_response_schema.timings)
    )
    assert all(i.remind_at <= task_create_schema.due_date for i in used_reminders)
    assert any(i.remind_at < task_create_schema.due_date for i in used_reminders)
