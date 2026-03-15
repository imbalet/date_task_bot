from datetime import UTC, datetime, timedelta
from typing import NotRequired, TypedDict
from uuid import UUID, uuid4

from date_task_bot.models import ReminderOrm
from date_task_bot.repositories.schemas import ReminderResponse
from date_task_bot.schemas import Reminder, ReminderStatus

from .factory import AbstractFactory


class ReminderFields(TypedDict):
    id: NotRequired[UUID]
    task_id: NotRequired[UUID]
    remind_at: NotRequired[datetime]
    status: NotRequired[ReminderStatus]
    offset_seconds: NotRequired[timedelta]


class ReminderFactory(AbstractFactory[ReminderFields, Reminder, ReminderOrm]):
    model_for_validation = ReminderResponse

    def make_schema(self, fields: ReminderFields | None = None) -> Reminder:
        if not fields:
            fields = {}
        return Reminder(
            id=fields.get("id") or uuid4(),
            task_id=fields.get("task_id") or uuid4(),
            remind_at=fields.get("remind_at") or datetime.now(UTC),
            status=fields.get("status", ReminderStatus.PENDING),
            offset_seconds=fields.get("offset_seconds", timedelta(hours=-1)),
        )

    def schema_to_orm(self, reminder: Reminder) -> ReminderOrm:
        orm = ReminderOrm(
            remind_at=reminder.remind_at,
            offset_seconds=reminder.offset_seconds,
            task_id=reminder.task_id,
        )
        orm.id = reminder.id
        orm.status = reminder.status
        return orm
