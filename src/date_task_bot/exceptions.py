from enum import StrEnum
from typing import Any


class EntityEnum(StrEnum):
    USER = "User"
    TASK = "Task"
    REMINDER = "Reminder"
    SETTINGS = "Settings"
    OTHER = "other"


class AppException(Exception):
    MESSAGE_TEMPLATE = "{entity}: {data}"

    def __init__(
        self,
        entity: EntityEnum,
        data: dict[str, Any] | None = None,
        *,
        message: str | None = None,
    ) -> None:
        self.entity = entity
        self.data = data or {}

        if message is None:
            message = self.MESSAGE_TEMPLATE.format(
                entity=entity.value,
                data=self._format_data(self.data),
            )

        super().__init__(message)

    @staticmethod
    def _format_data(data: dict[str, Any]) -> str:
        return ", ".join(f"{k}={v}" for k, v in data.items()) or "no data"


class AlreadyExistsException(AppException):
    MESSAGE_TEMPLATE = "{entity} with {data} already exists."


class NotFoundException(AppException):
    MESSAGE_TEMPLATE = "{entity} with {data} not found."


class ValidationException(AppException):
    MESSAGE_TEMPLATE = "Validation error for {entity}: {data}."
