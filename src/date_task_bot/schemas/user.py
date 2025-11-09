from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .task import Task
from .user_settings import UserSettings


class User(BaseModel):
    id: str
    created_at: datetime
    tasks: list[Task]
    settings: UserSettings | None = None

    model_config = ConfigDict(from_attributes=True)
