import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import PostgresDsn, EmailStr, UrlConstraints
from pydantic_core import MultiHostUrl, Url
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


APP_DIR_PATH = Path(os.path.abspath(__file__)).parent.parent.parent


def get_path(path: str) -> str:
    return str(APP_DIR_PATH.joinpath(path).resolve())

EmailDsn = Annotated[Url, UrlConstraints(allowed_schemes=["smtp", "smtp+ssl", "smtp+tls", "test"])]


class Settings(BaseSettings):
    PORT: int = 8000
    DEBUG: bool = False
    RUN_ENV: str = "dev"
    DATABASE_URL: PostgresDsn = MultiHostUrl("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    HOST: str = "localhost"
    DB_DEBUG: bool = False

    EMAIL_URL: EmailDsn = Url("smtp+tls://login:password@smtp_server:25")
    EMAIL_FROM: EmailStr = "info@coin-master.devsoft.pl"
    EMAIL_FROM_NAME: str = "Coin Master"

    PAGINATION_DEFAULT_LIMIT: int = 20

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings(_env_file=get_path(".env"))


settings = get_settings()
