from collections import defaultdict
from enum import Enum
from warnings import warn


class MsgKey(str, Enum):
    # control
    CANCEL = "cancel"
    BACK = "back"
    CONFIRM = "confirm"
    NEXT = "next"
    PREV = "prev"

    # texts
    DUE_DATE = "due_date"
    REMINDERS = "reminders"
    REMIND_TIME_PREFIX = "remind_time_prefix"
    TASK_REMINDER = "task_reminder"
    WITH_DUE_DATE = "with_due_date"
    REMAIN = "remain"


_TEXTS: dict[MsgKey, str] = {
    # control
    MsgKey.CANCEL: "Отмена",
    MsgKey.BACK: "Назад",
    MsgKey.CONFIRM: "Готово",
    MsgKey.NEXT: "Далее",
    MsgKey.PREV: "Назад",
    # texts
    MsgKey.DUE_DATE: "Дата выполнения",
    MsgKey.REMINDERS: "Напоминания",
    MsgKey.REMIND_TIME_PREFIX: ", за",
    MsgKey.TASK_REMINDER: "Напоминание о задаче",
    MsgKey.WITH_DUE_DATE: "c датой выполнения",
    MsgKey.REMAIN: "Осталось",
}


def missing_handler():
    warn("No translation for key", stacklevel=2)
    return "<?>"


TEXTS = defaultdict(missing_handler, _TEXTS)


def validate_texts():
    missing = set(MsgKey) - set(TEXTS.keys())
    extra = set(TEXTS.keys()) - set(MsgKey)

    if missing:
        warn(f"No text for: {missing}")

    if extra:
        warn(f"Extra key in TEXTS dict: {extra}")
