from date_task_bot.presentation.constants.templates import (
    TaskListItemTemplate,
    TaskShortTemplate,
    TaskTemplate,
)
from date_task_bot.repositories.schemas import PaginationResponse
from date_task_bot.schemas import Reminder, Task

from .base_formatter import BaseFormatterWithDate
from .datetime_formatter import DateFormat
from .reminder_formatter import ReminderFormatter


class TaskFormatter(BaseFormatterWithDate):
    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.reminder_formatter = ReminderFormatter(user_tz=user_tz)

    def _format_reminders(self, reminders: list[Reminder]) -> str:
        return "\n".join([self.reminder_formatter.format(i) for i in reminders])

    def format(self, model: Task) -> str:
        formatted_reminders = "\n".join(
            [self.reminder_formatter.format(i) for i in model.reminders]
        )
        return TaskTemplate(
            text=model.text,
            due_date=self.date_formatter.format(model.due_date, DateFormat.SHORT),
            reminders=formatted_reminders,
        ).render()


class TaskShortFormatter(BaseFormatterWithDate):
    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        return f"{text[:max_length]}{'...' if len(text) > max_length else ''}"

    def format(self, model: Task, max_text_length: int = 30) -> str:
        return TaskShortTemplate(
            text=self._truncate_text(model.text, max_text_length),
            due_date=self.date_formatter.format(model.due_date, DateFormat.SHORT),
        ).render()


class TaskListFormatter(BaseFormatterWithDate):
    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.task_formatter = TaskShortFormatter(user_tz=user_tz)

    def format(self, model: PaginationResponse[Task]) -> str:
        items = [
            TaskListItemTemplate(
                index=idx, task_text=self.task_formatter.format(task)
            ).render()
            for idx, task in enumerate(model.items, start=model.offset + 1)
        ]
        return "\n".join(items)
