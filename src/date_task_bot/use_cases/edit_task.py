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
        updated_reminders = []
        now = datetime.now(UTC)

        for reminder in reminders:
            offset = reminder.offset_seconds
            remind_at = new_due_date + offset
            if remind_at <= now:
                continue
            updated_reminders.append(
                reminder.model_copy(update={"remind_at": remind_at})
            )
        return updated_reminders

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

        task = await self.task_repo.get(id=data.id, load_reminders=True)
        if not task or task.user_id != data.user_id:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        updated_task = await self.task_repo.update(data=data)
        if not updated_task:
            raise NotFoundException(entity=EntityEnum.TASK, data={"id": data.id})

        if data.due_date is not None:
            updated_reminders = self.update_reminders(
                reminders=task.reminders, new_due_date=data.due_date
            )
            await self.reminder_repo.update_all(updated_reminders)
            updated_task = updated_task.model_copy(
                update={"reminders": updated_reminders}
            )
        else:
            updated_task = updated_task.model_copy(update={"reminders": task.reminders})

        return updated_task
