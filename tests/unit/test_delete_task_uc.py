import pytest

from date_task_bot.exceptions import NotFoundException
from date_task_bot.repositories.schemas import TaskResponse
from date_task_bot.use_cases import DeleteTaskUseCase


@pytest.fixture
def delete_task_uc(task_repo_mock):
    return DeleteTaskUseCase(task_repo=task_repo_mock)


async def test_delete(
    task_repo_mock,
    task_response_schema: TaskResponse,
    delete_task_uc: DeleteTaskUseCase,
):
    task_repo_mock.get.return_value = task_response_schema
    await delete_task_uc.execute(
        task_id=task_response_schema.id, user_id=task_response_schema.user_id
    )

    task_repo_mock.get.assert_awaited_once()
    task_repo_mock.delete.assert_awaited_once_with(id=task_response_schema.id)


async def test_delete_wrong_user(
    task_repo_mock,
    task_response_schema: TaskResponse,
    delete_task_uc: DeleteTaskUseCase,
):
    task_repo_mock.get.return_value = task_response_schema
    other_user_id = "other"

    with pytest.raises(NotFoundException):
        await delete_task_uc.execute(
            task_id=task_response_schema.id, user_id=other_user_id
        )

    task_repo_mock.get.assert_awaited_once()
    task_repo_mock.delete.assert_not_awaited()


async def test_delete_not_found(
    task_repo_mock,
    task_response_schema: TaskResponse,
    delete_task_uc: DeleteTaskUseCase,
):
    task_repo_mock.get.return_value = None

    with pytest.raises(NotFoundException):
        await delete_task_uc.execute(
            task_id=task_response_schema.id, user_id=task_response_schema.user_id
        )

    task_repo_mock.get.assert_awaited_once()
    task_repo_mock.delete.assert_not_awaited()
