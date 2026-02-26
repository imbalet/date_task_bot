from datetime import UTC, datetime

from date_task_bot.exceptions import EntityEnum, ValidationException
from date_task_bot.repositories import (
    TaskRepository,
    UserSettingsRepository,
)
from date_task_bot.repositories.schemas import ReminderCreate, TaskCreate
from date_task_bot.schemas import DefaultRemindTiming, Task


class CreateTaskUseCase:

    def __init__(
        self, task_repo: TaskRepository, user_settings_repo: UserSettingsRepository
    ) -> None:
        self.task_repo = task_repo
        self.user_settings_repo = user_settings_repo

    @staticmethod
    def create_reminders(
        due_date: datetime, timings: list[DefaultRemindTiming]
    ) -> list[ReminderCreate]:
        reminders = []
        now = datetime.now(UTC)

        for timing in timings:
            remind_at = due_date + timing.offset_seconds
            if remind_at <= now:
                continue

            reminders.append(
                ReminderCreate(
                    remind_at=remind_at, offset_seconds=timing.offset_seconds
                )
            )
        return reminders

    async def execute(
        self, user_id: str, text: str, due_date: datetime, now_: datetime | None = None
    ) -> Task:
        """Creates task with related timings and reminders.

        Args:
            user_id (str): User ID.
            text (str): Task description.
            due_date (datetime): Task due date.
            now_ (datetime | none, optional): Base now time. Defaults to None.

        Returns:
            Task: Created task.
        """
        due_date_utc = due_date.astimezone(UTC)
        now = now_ or datetime.now(UTC)
        if due_date_utc < now:
            raise ValidationException(
                EntityEnum.TASK, data={"due_date": "must be in future"}
            )
        user_settings = await self.user_settings_repo.get_by_user_id(
            user_id=user_id, load_offsets=True
        )
        reminders = self.create_reminders(
            due_date=due_date_utc, timings=user_settings.timings
        )
        task = await self.task_repo.create(
            TaskCreate(
                user_id=user_id,
                text=text,
                due_date=due_date_utc,
                reminders=reminders,
            )
        )
        return task
