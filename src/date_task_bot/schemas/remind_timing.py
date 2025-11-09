from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RemindTiming(BaseModel):
    id: str
    settings_id: UUID
    timing: timedelta

    model_config = ConfigDict(from_attributes=True)
