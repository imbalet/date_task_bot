from pydantic import BaseModel, ConfigDict


class BaseAppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
