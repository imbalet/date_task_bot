from dataclasses import dataclass
from datetime import UTC, datetime

from date_task_bot.repositories import (
    TaskRepository,
    UserSettingsRepository,
)
from date_task_bot.repositories.schemas import ReminderCreate, TaskCreate, TaskResponse


@dataclass
class CreateTaskUseCaseResult:
    task: TaskResponse


class CreateTaskUseCase:

    def __init__(
        self, task_repo: TaskRepository, user_settings_repo: UserSettingsRepository
    ) -> None:
        self.task_repo = task_repo
        self.user_settings_repo = user_settings_repo

    async def execute(
        self, user_id: str, text: str, due_date: datetime
    ) -> CreateTaskUseCaseResult:
        """Creates task with related timings and reminders.

        Args:
            user_id (str): _description_
            text (str): _description_
            due_date (datetime): _description_

        Returns:
            CreateTaskUseCaseResult: _description_
        """
        due_date_utc = due_date.astimezone(UTC)
        user_settings = await self.user_settings_repo.get_by_user_id(
            user_id=user_id, load_offsets=True
        )
        reminders = [
            ReminderCreate(
                remind_at=due_date_utc + t.offset_seconds,
                offset_seconds=t.offset_seconds,
            )
            for t in user_settings.offsets_seconds
        ]
        task = await self.task_repo.create(
            TaskCreate(
                user_id=user_id,
                text=text,
                due_date=due_date_utc,
                reminders=reminders,
            )
        )
        return CreateTaskUseCaseResult(task=task)
