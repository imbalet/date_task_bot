# ruff: noqa: E501
from collections import defaultdict
from enum import StrEnum
from warnings import warn


class MsgKey(StrEnum):
    # pagination
    CANCEL = "cancel"
    BACK = "back"
    CONFIRM = "confirm"
    NEXT = "next"
    PREV = "prev"

    # task actions
    DELETE = "delete"
    EDIT = "edit"
    MARK_AS_DONE = "mark_as_done"

    # texts
    DUE_DATE = "due_date"
    REMINDERS = "reminders"
    REMIND_TIME_PREFIX = "remind_time_prefix"
    TASK_REMINDER = "task_reminder"
    WITH_DUE_DATE = "with_due_date"
    REMAIN = "remain"

    YOUR_TASKS = "your_tasks"
    NO_TASKS = "no_tasks"

    CREATED_TASK = "created_task"
    DATE_OR_TEXT_NOT_FOUND = "date_or_text_not_found"

    WELCOME_MESSAGE = "welcome_message"
    YOUR_TIMEZONE = "your_timezone"
    CHANGE_TIMEZONE = "change_timezone"

    SELECT_TIMEZONE = "select_timezone"
    CURRENT_TIMEZONE = "current_timezone"
    CURRENT_TIME = "current_time"

    SEND_YOUR_TIMEZONE = "send_your_timezone"
    TIMEZONE_WAS_SET = "timezone_was_set"
    NO_TIMEZONE = "no_timezone"

    OTHER_TZ = "other_tz"

    # for tasks actions, results, etc
    TASK_DELETED = "task_deleted"
    CHOOSE_FIELD_TO_UPDATE = "choose_field"

    # exceptions
    UNEXPECTED_ERROR = "unexpected_error"
    NOT_FOUND_ERROR = "not_found_error"
    ALREADY_EXISTS_ERROR = "already_exists"
    VALIDATION_ERROR = "validation_error"

    # entities
    TASK = "task"
    USER = "user"
    USER_SETTINGS = "user_settings"
    REMINDER = "reminder"
    OTHER_ENTITY = "other_entity"

    # editing task, fields
    DUE_DATE_FIELD = "due_date_field"
    TEXT_FIELD = "text_field"

    SELECT_NEW_DUE_DATE = "select_new_due_date"
    SELECT_NEW_TEXT = "select_new_text"
    TEXT_NOT_FOUND = "text_not_found"
    DATE_PARSING_ERROR = "date_parsing_error"

    UPDATED_TASK = "updated_task"


_TEXTS: dict[MsgKey, str] = {
    # pagination
    MsgKey.CANCEL: "Отмена",
    MsgKey.BACK: "Назад",
    MsgKey.CONFIRM: "Готово",
    MsgKey.NEXT: "Далее",
    MsgKey.PREV: "Назад",
    # task actions
    MsgKey.DELETE: "Удалить",
    MsgKey.EDIT: "Изменить",
    MsgKey.MARK_AS_DONE: "Сделано",
    # texts
    MsgKey.DUE_DATE: "Дата выполнения",
    MsgKey.REMINDERS: "Напоминания",
    MsgKey.REMIND_TIME_PREFIX: ", за",
    MsgKey.TASK_REMINDER: "Напоминание о задаче",
    MsgKey.WITH_DUE_DATE: "c датой выполнения",
    MsgKey.REMAIN: "Осталось",
    MsgKey.YOUR_TASKS: "Ваши задачи",
    MsgKey.NO_TASKS: "У вас нет задач",
    MsgKey.CREATED_TASK: "Создана задача",
    MsgKey.DATE_OR_TEXT_NOT_FOUND: "Не найдена дата или текст",
    MsgKey.WELCOME_MESSAGE: "Привет, это бот для задач",
    MsgKey.YOUR_TIMEZONE: "Ваш текущий часовой пояс",
    MsgKey.CHANGE_TIMEZONE: "Для смены используйте команду /timezone",
    MsgKey.SELECT_TIMEZONE: "Выберите свой часовой пояс",
    MsgKey.CURRENT_TIMEZONE: "Текущий часовой пояс",
    MsgKey.CURRENT_TIME: "Текущее время",
    MsgKey.SEND_YOUR_TIMEZONE: "Напишите ваш часовой пояс по стандарту IANA",
    MsgKey.TIMEZONE_WAS_SET: "Часовой пояс установлен",
    MsgKey.NO_TIMEZONE: "Такого часового пояса нет. Попробуйте выбрать из списка популярных или напишите корректно.",
    MsgKey.OTHER_TZ: "Другой",
    MsgKey.TASK_DELETED: "Задача была удалена",
    MsgKey.CHOOSE_FIELD_TO_UPDATE: "Выберете поле для изменения",
    MsgKey.UNEXPECTED_ERROR: "Произошла непредвиденная ошибка.",
    MsgKey.NOT_FOUND_ERROR: "{entity} with {data} not found.",
    MsgKey.ALREADY_EXISTS_ERROR: "{entity} with {data} already exists.",
    MsgKey.VALIDATION_ERROR: "Ошибка валидации для {entity}: {data}.",
    MsgKey.TASK: "Задача",
    MsgKey.USER: "Пользователь",
    MsgKey.USER_SETTINGS: "Настройки пользователя",
    MsgKey.REMINDER: "Напоминание",
    MsgKey.OTHER_ENTITY: "Неизвестная сущность",
    MsgKey.SELECT_NEW_DUE_DATE: "Введите новую дату и время в формате дд.мм.гг чч:мм. Например, 14.05.25 16:51",
    MsgKey.SELECT_NEW_TEXT: "Введите новый текст задачи.",
    MsgKey.TEXT_NOT_FOUND: "Текст не найден",
    MsgKey.DATE_PARSING_ERROR: "Ошибка парсинга даты",
    MsgKey.UPDATED_TASK: "Задача была обновлена",
    MsgKey.DUE_DATE_FIELD: "Дата выполнения",
    MsgKey.TEXT_FIELD: "Текст",
}


def missing_handler() -> str:
    warn("No translation for key", stacklevel=2)
    return "<?>"


TEXTS = defaultdict(missing_handler, _TEXTS)


def validate_texts() -> None:
    missing = set(MsgKey) - set(TEXTS.keys())
    extra = set(TEXTS.keys()) - set(MsgKey)

    if missing:
        warn(f"No text for: {missing}", stacklevel=2)

    if extra:
        warn(f"Extra key in TEXTS dict: {extra}", stacklevel=2)
