from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import NotRequired, TypedDict
from uuid import uuid4

from date_task_bot.models import UserOrm
from date_task_bot.repositories.schemas import UserResponse
from date_task_bot.schemas import Task, User, UserSettings

from .factory import AbstractFactory
from .task_factory import TaskFactory
from .user_settings_factory import UserSettingsFactory


class UserFields(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[datetime]
    tasks: NotRequired[list[Task]]
    settings: NotRequired[UserSettings | None]


class UserFactory(AbstractFactory[UserFields, User, UserOrm]):
    model_for_validation = UserResponse

    def __init__(
        self, insert_async_func: Callable[[UserOrm], Awaitable[UserOrm]] | None = None
    ) -> None:
        super().__init__(insert_async_func)
        self.task_factory = TaskFactory()
        self.user_settings_factory = UserSettingsFactory()

    def make_schema(
        self,
        fields: UserFields | None = None,
        use_default_settings: bool = False,
    ) -> User:
        if not fields:
            fields = {}
        user_id = fields.get("id", str(uuid4()))
        settings = fields.get("settings")
        tasks = fields.get("tasks")
        if settings:
            settings.user_id = user_id
        elif use_default_settings:
            settings = self.user_settings_factory.make_schema(
                {"user_id": user_id}, use_default_offsets=True
            )
        if tasks:
            tasks = [
                i.model_copy(update={"user_id": user_id}, deep=True) for i in tasks
            ]

        return User(
            id=user_id,
            created_at=fields.get("created_at", datetime.now(UTC)),
            tasks=tasks or [],
            settings=settings,
        )

    def schema_to_orm(self, user: User) -> UserOrm:
        orm = UserOrm(
            id=user.id,
            settings=self.user_settings_factory.schema_to_orm(user.settings)
            if user.settings
            else None,
        )
        orm.id = user.id
        orm.created_at = user.created_at
        orm.tasks = list(map(self.task_factory.schema_to_orm, user.tasks))
        return orm
