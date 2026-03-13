from datetime import UTC, datetime
from uuid import uuid4

from date_task_bot.schemas import Task, User, UserSettings

from .user_settings_factory import make_user_settings


def make_user(
    *,
    id: str | None = None,
    created_at: datetime | None = None,
    tasks: list[Task] | None = None,
    settings: UserSettings | None = None,
    use_default_settings: bool = False,
) -> User:
    user_id = id or str(uuid4())
    if settings:
        settings.user_id = user_id
    elif use_default_settings:
        settings = make_user_settings(user_id=user_id, use_default_offsets=True)
    if tasks:
        tasks = [i.model_copy(update={"user_id": user_id}, deep=True) for i in tasks]

    return User(
        id=user_id,
        created_at=created_at or datetime.now(UTC),
        tasks=tasks or [],
        settings=settings,
    )
