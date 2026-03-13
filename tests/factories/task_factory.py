from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from date_task_bot.schemas import Reminder, Task, TaskStatus


def make_task(
    *,
    id: UUID | None = None,
    user_id: str = "123",
    text: str = "text",
    due_date: datetime | None = None,
    status: TaskStatus = TaskStatus.PENDING,
    created_at: datetime | None = None,
    edited_at: datetime | None = None,
    reminders: list[Reminder] | None = None,
    prefer_offset: bool = True,
) -> Task:
    task_id = id or uuid4()
    due_date = due_date or datetime.now(UTC) + timedelta(days=1)

    reminders = reminders or []
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
        user_id=user_id,
        text=text,
        due_date=due_date,
        status=status,
        created_at=created_at or datetime.now(UTC),
        edited_at=edited_at,
        reminders=validated_reminders,
    )
