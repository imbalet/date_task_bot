ALREADY_EXISTS_MESSAGE = "{entity} is already exists."
NOT_FOUND_MESSAGE = "{entity} not found."
UNEXPECTED_ERROR = "Unexpected database error."


class AppException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AlreadyExistsException(AppException):
    pass


class NotFoundException(AppException):
    pass
