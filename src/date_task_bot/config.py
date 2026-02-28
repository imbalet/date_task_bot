from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevels(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Config(BaseSettings):
    LOG_LEVEL: LogLevels = LogLevels.INFO

    BOT_TOKEN: str

    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None

    SQLITE_DB_NAME: str = "database"

    @property
    def DB_URL(self) -> str:  # noqa: N802
        if self.DB_HOST:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"sqlite+aiosqlite:///./database/{self.SQLITE_DB_NAME}.db"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


_config_instance = None


def get_config() -> Config:
    global _config_instance

    if _config_instance is None:
        _config_instance = Config()  # pyright: ignore
    return _config_instance
