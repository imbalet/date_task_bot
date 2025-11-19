from datetime import UTC, datetime

from date_task_bot.presentation.constants.templates import (
    ReminderWithDeltaTemplate,
    ReminderWithoutDeltaTemplate,
)
from date_task_bot.schemas import Reminder

from .base_formatter import BaseFormatterWithDate
from .datetime_formatter import DateFormat, TimeDeltaFormatter


class ReminderFormatter(BaseFormatterWithDate):

    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.delta_formatter = TimeDeltaFormatter()

    def format(self, model: Reminder) -> str:
        now = datetime.now(UTC)
        date_format = (
            DateFormat.SHORT_NO_YEAR
            if now.year == model.remind_at.year
            else DateFormat.SHORT
        )

        date_formatted = self.date_formatter.format(model.remind_at, date_format)
        delta_formatted = self.delta_formatter.format(model.offset_seconds)

        if delta_formatted:
            return ReminderWithDeltaTemplate(
                delta=delta_formatted, date=date_formatted
            ).render()
        return ReminderWithoutDeltaTemplate(date=date_formatted).render()
