from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    TEST_DB_HOST: str | None = None
    TEST_DB_PORT: int | None = None
    TEST_DB_NAME: str | None = None
    TEST_DB_USER: str | None = None
    TEST_DB_PASS: str | None = None

    @property
    def DB_URL(self) -> str:  # noqa: N802
        if self.TEST_DB_HOST:
            return (
                f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@"
                f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
            )
        else:
            return "sqlite+aiosqlite:///:memory:"

    model_config = SettingsConfigDict(env_file="tests/.env.test")


_config_instance = None


def get_config() -> Config:
    global _config_instance

    if _config_instance is None:
        _config_instance = Config()  # type: ignore
    return _config_instance
