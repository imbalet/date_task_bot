from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .task import Task


class User(BaseModel):
    id: str
    created_at: datetime
    tasks: list[Task]

    model_config = ConfigDict(from_attributes=True)
