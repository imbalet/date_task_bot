from datetime import datetime

from .base_schema import BaseAppSchema
from .task import Task
from .user_settings import UserSettings


class User(BaseAppSchema):
    id: str
    created_at: datetime
    tasks: list[Task]
    settings: UserSettings | None
