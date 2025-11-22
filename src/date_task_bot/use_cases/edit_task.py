from datetime import UTC, datetime

from date_task_bot.exceptions import EntityEnum, NotFoundException, ValidationException
from date_task_bot.repositories import ReminderRepository, TaskRepository
from date_task_bot.repositories.schemas import TaskUpdate
from date_task_bot.schemas import Reminder, Task


class EditTaskUseCase:

    def __init__(
        self, task_repo: TaskRepository, reminder_repo: ReminderRepository
    ) -> None:
        self.task_repo = task_repo
        self.reminder_repo = reminder_repo

    @staticmethod
    def update_reminders(
        reminders: list[Reminder], new_due_date: datetime
    ) -> list[Reminder]:
        reminders = []
        now = datetime.now(UTC)

        for reminder in reminders:
            offset = reminder.offset_seconds
            remind_at = new_due_date + offset
            if remind_at <= now:
                continue
            reminders.append(reminder.model_copy(update={"remind_at": remind_at}))
        return reminders

    async def execute(self, data: TaskUpdate) -> Task:
        now = datetime.now(UTC)

        if data.due_date and data.due_date <= now:
            raise ValidationException(
                EntityEnum.TASK,
                data={
                    "due_date": data.due_date,
                    "message": "Date must be in the future",
                },
            )

        due_date_changed = data.due_date is not None

        task = await self.task_repo.get(id=data.id, load_reminders=due_date_changed)
        if not task or task.user_id != data.user_id:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        updated_task = await self.task_repo.update(data=data)

        if due_date_changed and data.due_date is not None:
            updated_reminders = self.update_reminders(
                reminders=task.reminders, new_due_date=data.due_date
            )
            await self.reminder_repo.update_all(updated_reminders)
        if not updated_task:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        return updated_task
