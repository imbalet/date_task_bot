from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BaseRepository(ABC):  # noqa: B024
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
