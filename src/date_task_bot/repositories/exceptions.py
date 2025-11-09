ALREADY_EXISTS_MESSAGE = "{entity} is already exists."
NOT_FOUND_MESSAGE = "{entity} not found."
UNEXPECTED_ERROR = "Unexpected database error."


class RepositoryException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AlreadyExistsException(RepositoryException):
    pass


class NotFoundException(RepositoryException):
    pass
