import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import (
    EmailStr,
    PostgresDsn,
    UrlConstraints,
    field_validator,
)
from pydantic_core import (
    MultiHostUrl,
    Url,
)
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

    # Storage (S3-compatible: MinIO lokalnie, AWS S3 na produkcji)
    AWS_REGION_NAME: str = "us-east-1"
    AWS_ACCESS_KEY: str = ""
    AWS_ACCESS_KEY_SECRET: str = ""
    AWS_S3_BUCKET_NAME: str = "coin-master"
    AWS_S3_BUCKET_URL: str = ""
    AWS_ENDPOINT_URL: str = ""  # puste = AWS; "http://minio:9000" = MinIO

    # Czasy życia linków (sekundy)
    SCAN_URL_EXPIRES_IN: int = 900  # 15 min — podgląd w aplikacji
    SHARE_URL_EXPIRES_IN: int = 604800  # 7 dni — maksimum AWS SigV4

    # Hosty dozwolone przez TrustedHostMiddleware
    ALLOWED_HOSTS: list[str] = ["coin-master.devsoft.pl", "localhost", "api", "127.0.0.1"]

    model_config = SettingsConfigDict(env_file=".env")

    @field_validator("SHARE_URL_EXPIRES_IN")
    @classmethod
    def validate_share_url_expires_in(cls, value: int) -> int:
        if value > 604800:
            raise ValueError("SHARE_URL_EXPIRES_IN nie może przekroczyć 604800 s (limit AWS SigV4)")
        return value


@lru_cache()
def get_settings():
    return Settings(_env_file=get_path(".env"))


settings = get_settings()
