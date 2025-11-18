from datetime import UTC, datetime, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

from babel.dates import format_datetime, format_timedelta

from date_task_bot.repositories.schemas import DueReminder, PaginationResponse
from date_task_bot.schemas import Reminder, Task


class DateFormat(StrEnum):
    SHORT = "EEE, d MMM y 'г.' HH:mm"
    SHORT_NO_YEAR = "EEE, d MMM HH:mm"


class DateFormatter:
    def __init__(self, timezone: str = "UTC") -> None:
        self.timezone = timezone

    def _date_to_tz(self, date: datetime) -> datetime:
        return date.astimezone(ZoneInfo(self.timezone))

    def _format_date(self, date: datetime, format: str) -> str:
        return format_datetime(self._date_to_tz(date), format, locale="ru")

    def format(self, date: datetime, fmt: DateFormat) -> str:
        return self._format_date(date, fmt.value)


class TimeDeltaFormatter:
    def format(self, delta: timedelta):
        if abs(delta.total_seconds()) < 60:
            return ""
        return format_timedelta(
            delta, locale="ru", granularity="minute", threshold=1, format="short"
        )


class BaseFormatterWithDate:
    def __init__(self, user_tz: str) -> None:
        self.date_formatter = DateFormatter(user_tz)


class DueReminderFormatter(BaseFormatterWithDate):
    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.delta_formatter = TimeDeltaFormatter()

    def format(self, model: DueReminder) -> str:
        delta_time = model.due_date - datetime.now(UTC)
        delta_formatted = self.delta_formatter.format(delta_time)
        delta_text = ""
        if delta_formatted:
            delta_text = f"\nОсталось {delta_formatted}"
        return f"""\
Напоминание о задаче
<code>{model.text}</code>
c датой выполнения:
<b>{self.date_formatter.format(model.due_date, DateFormat.SHORT)}</b>{delta_text}"""


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
        delta_formatted = self.delta_formatter.format(model.offset_seconds)
        delta_text = ""
        if delta_formatted:
            delta_text = f", за {delta_formatted}"
        return f"""\
{self.date_formatter.format(model.remind_at, date_format)}{delta_text}"""


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

        return f"""\
<code>{model.text}</code>
Дата выполнения:
<b>{self.date_formatter.format(model.due_date, DateFormat.SHORT)}</b>
Напоминания:
{formatted_reminders}"""


class TaskShortFormatter(BaseFormatterWithDate):
    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        return f"{text[:max_length]}{'...' if len(text) > max_length else ''}"

    def format(self, model: Task, max_text_length: int = 30) -> str:
        return f"""\
<code>{self._truncate_text(model.text, max_text_length)}</code> \
<b>{self.date_formatter.format(model.due_date, DateFormat.SHORT)}</b>"""


class TaskListFormatter(BaseFormatterWithDate):
    def __init__(self, user_tz: str) -> None:
        super().__init__(user_tz)
        self.task_formatter = TaskShortFormatter(user_tz=user_tz)

    def format(self, model: PaginationResponse[Task]) -> str:
        formatted_tasks = "\n".join(
            [
                f"{idx}. {self.task_formatter.format(el)}"
                for idx, el in enumerate(model.items, start=model.offset + 1)
            ]
        )

        return formatted_tasks
