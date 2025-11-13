from dataclasses import dataclass
from datetime import datetime

from date_task_bot.repositories import (
    TaskRepository,
    UserSettingsRepository,
)
from date_task_bot.repositories.schemas import (
    ReminderCreate,
    TaskCreate,
    TaskRemindTimingCreate,
    TaskResponse,
)


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
        user_settings = await self.user_settings_repo.get_by_user_id(
            user_id=user_id, load_timings=True
        )
        timings = [
            TaskRemindTimingCreate(timing=t.timing) for t in user_settings.timings
        ]
        reminders = [
            ReminderCreate(remind_at=due_date + t.timing) for t in user_settings.timings
        ]
        task = await self.task_repo.create(
            TaskCreate(
                user_id=user_id,
                text=text,
                due_date=due_date,
                timings=timings,
                reminders=reminders,
            )
        )
        return CreateTaskUseCaseResult(task=task)
