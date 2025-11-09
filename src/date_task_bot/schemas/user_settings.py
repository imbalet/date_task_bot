from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .remind_timing import RemindTiming


class UserSettings(BaseModel):
    id: UUID
    user_id: str
    timezone: str
    timings: list[RemindTiming]

    model_config = ConfigDict(from_attributes=True)
