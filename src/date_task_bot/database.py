from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from date_task_bot.config import get_config
from date_task_bot.models import Base


def ensure_sqlite_dir(db_url: str) -> None:
    url = make_url(db_url)

    if url.drivername.startswith("sqlite") and url.database:
        db_path = Path(url.database)

        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path

        db_path.parent.mkdir(parents=True, exist_ok=True)


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_sessionmaker() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    db_url = get_config().DB_URL

    ensure_sqlite_dir(db_url)

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        future=True,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def enable_sqlite_fk(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    return engine, async_session
