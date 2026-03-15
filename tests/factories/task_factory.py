from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import NotRequired, TypedDict
from uuid import UUID, uuid4

from date_task_bot.models import TaskOrm
from date_task_bot.repositories.schemas import TaskResponse
from date_task_bot.schemas import Reminder, Task, TaskStatus

from .factory import AbstractFactory
from .reminder_factory import ReminderFactory


class TaskFields(TypedDict):
    id: NotRequired[UUID]
    user_id: NotRequired[str]
    text: NotRequired[str]
    due_date: NotRequired[datetime]
    status: NotRequired[TaskStatus]
    created_at: NotRequired[datetime]
    edited_at: NotRequired[datetime | None]
    reminders: NotRequired[list[Reminder]]


class TaskFactory(AbstractFactory[TaskFields, Reminder, TaskOrm]):
    model_for_validation = TaskResponse

    def __init__(
        self, insert_async_func: Callable[[TaskOrm], Awaitable[TaskOrm]] | None = None
    ) -> None:
        super().__init__(insert_async_func)
        self.reminder_factory = ReminderFactory()

    def make_schema(
        self,
        fields: TaskFields | None = None,
        prefer_offset: bool = True,
    ) -> Task:
        if not fields:
            fields = {}

        task_id = fields.get("id", uuid4())
        due_date = fields.get("due_date", datetime.now(UTC) + timedelta(days=1))

        reminders = fields.get("reminders", [])
        validated_reminders = []
        for reminder in reminders:
            if prefer_offset:
                update = {
                    "task_id": task_id,
                    "remind_at": due_date + reminder.offset_seconds,
                }
            else:
                update = {
                    "task_id": task_id,
                    "offset_seconds": reminder.remind_at - due_date,
                }
            validated_reminder = reminder.model_copy(update=update, deep=True)
            validated_reminders.append(validated_reminder)

        return Task(
            id=task_id,
            user_id=fields.get("user_id", "123"),
            text=fields.get("text", "text"),
            due_date=due_date,
            status=fields.get("status", TaskStatus.PENDING),
            created_at=fields.get("created_at", datetime.now(UTC)),
            edited_at=fields.get("edited_at"),
            reminders=validated_reminders,
        )

    def schema_to_orm(self, task: Task) -> TaskOrm:
        orm = TaskOrm(
            user_id=task.user_id,
            text=task.text,
            due_date=task.due_date,
            reminders=list(map(self.reminder_factory.schema_to_orm, task.reminders)),
        )
        orm.status = task.status
        orm.created_at = task.created_at
        orm.edited_at = task.edited_at  # type: ignore
        orm.id = task.id
        return orm
