from datetime import UTC, datetime

from date_task_bot.presentation.constants.templates import (
    DueReminderWithDeltaTemplate,
    DueReminderWithoutDeltaTemplate,
)
from date_task_bot.repositories.schemas import DueReminder

from .base_formatter import BaseFormatterWithDate
from .datetime_formatter import DateFormat, TimeDeltaFormatter


class DueReminderFormatter(BaseFormatterWithDate):
    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.delta_formatter = TimeDeltaFormatter()

    def format(self, model: DueReminder) -> str:
        delta_time = model.due_date - datetime.now(UTC)
        delta_formatted = self.delta_formatter.format(delta_time)
        date_formatted = self.date_formatter.format(model.due_date, DateFormat.SHORT)

        if delta_formatted:
            return DueReminderWithDeltaTemplate(
                text=model.text, due_date=date_formatted, delta=delta_formatted
            ).render()
        return DueReminderWithoutDeltaTemplate(
            text=model.text, due_date=date_formatted
        ).render()
