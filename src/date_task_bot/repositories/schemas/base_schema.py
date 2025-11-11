from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict
from sqlalchemy import inspect


def ensure_timezone(d: datetime | None) -> datetime | None:
    if d is None:
        return None

    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=UTC)
    return d


AwareDatetime = Annotated[datetime, AfterValidator(ensure_timezone)]
OptionalAwareDatetime = Annotated[datetime | None, AfterValidator(ensure_timezone)]


class RepositoryDTO(BaseModel):

    @classmethod
    def model_validate(cls, obj, **kwargs):
        def serialize(obj):
            if not hasattr(obj, "__mapper__"):
                return obj

            insp = inspect(obj)
            data = {}
            for name in insp.attrs.keys():
                if name in insp.unloaded:
                    continue
                try:
                    value = getattr(obj, name)
                    if hasattr(value, "__mapper__"):
                        value = serialize(value)
                    elif isinstance(value, list):
                        value = [
                            serialize(v) if hasattr(v, "__mapper__") else v
                            for v in value
                        ]
                    data[name] = value
                except Exception:
                    continue
            return data

        if not hasattr(obj, "__mapper__"):
            return super().model_validate(obj, **kwargs)

        data = serialize(obj)
        return super().model_validate(data, **kwargs)

    model_config = ConfigDict(from_attributes=True)
