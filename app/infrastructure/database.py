import logging

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.conf import settings


logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.DATABASE_URL.unicode_string(),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=8,
    max_overflow=16,
)

async_session = async_sessionmaker(
    async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_async_session():
    return async_session
