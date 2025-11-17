from datetime import UTC, datetime

from date_task_bot.schemas import Task, User, UserSettings

from .user_settings_factory import make_user_settings


def make_user(
    *,
    id: str = "123",
    created_at: datetime | None = None,
    tasks: list[Task] | None = None,
    settings: UserSettings | None = None,
    use_default_settings: bool = False,
) -> User:
    if settings:
        settings.user_id = id
    elif use_default_settings:
        settings = make_user_settings(user_id=id, use_default_offsets=True)
    if tasks:
        tasks = [i.model_copy(update={"user_id": id}, deep=True) for i in tasks]

    return User(
        id=id,
        created_at=created_at or datetime.now(UTC),
        tasks=tasks or [],
        settings=settings,
    )
