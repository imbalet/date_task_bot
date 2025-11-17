from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from date_task_bot.schemas import Reminder, ReminderStatus


def make_reminder(
    *,
    id: UUID | None = None,
    task_id: UUID | None = None,
    remind_at: datetime | None = None,
    status: ReminderStatus = ReminderStatus.PENDING,
    offset_seconds: timedelta = timedelta(hours=-1),
) -> Reminder:
    return Reminder(
        id=id or uuid4(),
        task_id=task_id or uuid4(),
        remind_at=remind_at or datetime.now(UTC),
        status=status,
        offset_seconds=offset_seconds,
    )
