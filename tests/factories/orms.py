from date_task_bot.models import (
    DefaultRemindTimingOrm,
    ReminderOrm,
    TaskOrm,
    UserOrm,
    UserSettingsOrm,
)
from date_task_bot.schemas import (
    DefaultRemindTiming,
    Reminder,
    Task,
    User,
    UserSettings,
)


def _set_orm_fields(orm, data):
    for k, v in data.items():
        setattr(orm, k, v)
    return orm


def make_default_timing_orm(
    default_timing: DefaultRemindTiming, **kwargs
) -> DefaultRemindTimingOrm:
    orm = DefaultRemindTimingOrm(
        offset_seconds=default_timing.offset_seconds,
        settings_id=default_timing.settings_id,
    )
    return _set_orm_fields(orm, kwargs)


def make_user_settings_orm(user_settings: UserSettings, **kwargs) -> UserSettingsOrm:
    orm = UserSettingsOrm(
        timings=list(map(make_default_timing_orm, user_settings.timings)),
        user_id=user_settings.user_id,
    )
    return _set_orm_fields(orm, kwargs)


def make_user_orm(user: User, **kwargs) -> UserOrm:
    orm = UserOrm(
        id=user.id,
        settings=make_user_settings_orm(user.settings) if user.settings else None,
    )
    return _set_orm_fields(orm, kwargs)


def make_reminder_orm(reminder: Reminder, **kwargs) -> ReminderOrm:
    orm = ReminderOrm(
        remind_at=reminder.remind_at,
        offset_seconds=reminder.offset_seconds,
        task_id=reminder.task_id,
    )
    return _set_orm_fields(orm, kwargs)


def make_task_orm(task: Task, **kwargs) -> TaskOrm:
    orm = TaskOrm(
        user_id=task.user_id,
        text=task.text,
        due_date=task.due_date,
        reminders=list(map(make_reminder_orm, task.reminders)),
    )
    return _set_orm_fields(orm, kwargs)
