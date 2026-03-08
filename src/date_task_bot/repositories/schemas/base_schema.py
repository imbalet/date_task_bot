from datetime import UTC, datetime
from logging import getLogger
from typing import Annotated, Any, Self

from pydantic import AfterValidator, BaseModel, ConfigDict
from sqlalchemy import inspect

logger = getLogger(__name__)


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
    def model_validate(cls, obj: Any, **kwargs: Any) -> Self:
        def serialize(obj: Any) -> dict[str, Any]:
            if not hasattr(obj, "__mapper__"):
                return obj  # type: ignore

            insp = inspect(obj)
            data = {}
            for name in insp.attrs.keys():  # noqa: SIM118
                if name in insp.unloaded:
                    continue
                value = None
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
                    logger.warning(
                        f"Error convert orm {type(obj)} field {name}"
                        + f"with value {value} to pydantic dto"
                    )
                    continue
            return data

        if not hasattr(obj, "__mapper__"):
            return super().model_validate(obj, **kwargs)

        data = serialize(obj)
        return super().model_validate(data, **kwargs)

    model_config = ConfigDict(from_attributes=True)
