import inspect
from unittest.mock import AsyncMock, create_autospec

import pytest

from date_task_bot.repositories import (
    ReminderRepository,
    TaskRepository,
    UserRepository,
    UserSettingsRepository,
)


@pytest.fixture
def repos_mock_factory():
    def _make_mock(cls):
        mock = create_autospec(cls, instance=True)
        for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
            if inspect.iscoroutinefunction(member):
                setattr(mock, name, AsyncMock())
        return mock

    return _make_mock


@pytest.fixture
def task_repo_mock(repos_mock_factory):
    return repos_mock_factory(TaskRepository)


@pytest.fixture
def user_repo_mock(repos_mock_factory):
    return repos_mock_factory(UserRepository)


@pytest.fixture
def reminder_repo_mock(repos_mock_factory):
    return repos_mock_factory(ReminderRepository)


@pytest.fixture
def user_settings_repo_mock(repos_mock_factory):
    return repos_mock_factory(UserSettingsRepository)
