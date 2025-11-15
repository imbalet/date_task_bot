import pytest

from date_task_bot.repositories.schemas import TaskCreate, TaskResponse
from date_task_bot.schemas import UserSettings
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
    user_settings_response_schema: UserSettings,
    task_response_schema: TaskResponse,
):
    user_settings_repo_mock.get_by_user_id.return_value = user_settings_response_schema
    task_repo_mock.create.return_value = task_response_schema

    res = await create_task_uc.execute(
        user_id=task_create_schema.user_id,
        text=task_create_schema.text,
        due_date=task_create_schema.due_date,
    )

    used_reminders = task_repo_mock.create.call_args[0][0].reminders

    assert res.task == task_response_schema

    assert all(
        used.offset_seconds == actual.offset_seconds
        for used, actual in zip(
            used_reminders, user_settings_response_schema.offsets_seconds
        )
    )
    assert all(i.remind_at <= task_create_schema.due_date for i in used_reminders)
    assert any(i.remind_at < task_create_schema.due_date for i in used_reminders)
