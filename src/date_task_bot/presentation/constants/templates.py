from dataclasses import dataclass

from date_task_bot.presentation.constants import TEXTS

from .text import MsgKey

# Task


@dataclass
class TaskTemplate:
    text: str
    due_date: str
    reminders: str

    def render(self) -> str:
        return f"""\
<code>{self.text}</code>
{TEXTS[MsgKey.DUE_DATE]}:
<b>{self.due_date}</b>
{TEXTS[MsgKey.REMINDERS]}:
{self.reminders}"""


@dataclass
class TaskShortTemplate:
    text: str
    due_date: str

    def render(self) -> str:
        return f"""\
<code>{self.text}</code> \
<b>{self.due_date}</b>"""


@dataclass
class TaskListItemTemplate:
    index: int
    task_text: str

    def render(self) -> str:
        return f"""\
{self.index}. {self.task_text}"""


# Reminder


@dataclass
class ReminderWithDeltaTemplate:
    delta: str
    date: str

    def render(self) -> str:
        return f"{self.date}{TEXTS[MsgKey.REMIND_TIME_PREFIX]} {self.delta}"


@dataclass
class ReminderWithoutDeltaTemplate:
    date: str

    def render(self) -> str:
        return f"{self.date}"


# DueReminder


@dataclass
class DueReminderWithDeltaTemplate:
    text: str
    due_date: str
    delta: str

    def render(self) -> str:
        return f"""\
{TEXTS[MsgKey.TASK_REMINDER]}
<code>{self.text}</code>
{TEXTS[MsgKey.WITH_DUE_DATE]}:
<b>{self.due_date}</b>
{TEXTS[MsgKey.REMAIN]} {self.delta}"""


@dataclass
class DueReminderWithoutDeltaTemplate:
    text: str
    due_date: str

    def render(self) -> str:
        return f"""\
{TEXTS[MsgKey.TASK_REMINDER]}
<code>{self.text}</code>
{TEXTS[MsgKey.WITH_DUE_DATE]}:
<b>{self.due_date}</b>"""


# Timezone


@dataclass
class TimezoneTemplate:
    timezone: str

    def render(self) -> str:
        return f"<code>{self.timezone}</code>"
