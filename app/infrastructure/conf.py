import os
from functools import lru_cache
from pathlib import Path

from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


APP_DIR_PATH = Path(os.path.abspath(__file__)).parent.parent.parent


def get_path(path: str) -> str:
    return str(APP_DIR_PATH.joinpath(path).resolve())


class Settings(BaseSettings):
    PORT: int = 8000
    DEBUG: bool = False
    RUN_ENV: str = "dev"
    DATABASE_URL: PostgresDsn = MultiHostUrl("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    HOST: str = "localhost"
    DB_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings(_env_file=get_path(".env"))


settings = get_settings()