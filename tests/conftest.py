from logging.config import dictConfig
from typing import (
    AsyncGenerator,
    Iterable,
)

import httpx
import pytest
import pytest_asyncio
from dependency_injector import providers
from httpx import (
    ASGITransport,
    AsyncClient,
)
from httpx_ws.transport import ASGIWebSocketTransport
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.domain.common.base import Base
from app.infrastructure.app import initialize_app
from app.infrastructure.conf import (
    Settings,
    settings,
)
from app.infrastructure.di.app_container import init_di
from app.infrastructure.logger import LogConfig
from app.infrastructure.storage.base import IStorageRepository
from app.infrastructure.storage.fake_s3 import FakeS3StorageRepository


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

pytestmark = pytest.mark.asyncio

pytest_plugins = []


async def load_spatialite(conn: AsyncConnection):
    raw_conn = await conn.get_raw_connection()
    driver_conn = raw_conn.driver_connection

    if not driver_conn:
        raise ValueError("Could not get the driver connection")

    try:
        await driver_conn.enable_load_extension(True)
        await driver_conn.load_extension(settings.SPATIALITE_LIBRARY_PATH)

        res = await (await driver_conn.execute("SELECT CheckSpatialMetaData();")).fetchone()
        if res[0] < 1:
            await driver_conn.execute("SELECT InitSpatialMetaData();")

    finally:
        # Disable extension loading
        await driver_conn.enable_load_extension(False)


@pytest_asyncio.fixture(scope="function", name="async_session")
async def async_session_fixture() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        async_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    async with async_session():
        async with async_engine.begin() as conn:
            await load_spatialite(conn)
            await conn.run_sync(Base.metadata.create_all)

        yield async_session

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture
async def default_session(async_session):
    async with async_session.begin() as session:
        return session


@pytest_asyncio.fixture
def session(async_session) -> Iterable[AsyncSession]:
    yield async_session


@pytest.fixture(scope="function")
def app(async_session):
    log_config = LogConfig().model_dump()
    dictConfig(log_config)

    di_container = init_di()
    di_container.config.override(providers.Singleton(Settings, EMAIL_URL="test://"))
    di_container.session.override(providers.Resource(lambda: async_session))
    di_container.services.storage.override(providers.Singleton(FakeS3StorageRepository))

    application = initialize_app(di_container)
    return application


@pytest.fixture(scope="function")
async def async_client(app):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest.fixture(scope="function")
async def async_ws_client(app):
    async with httpx.AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        yield client


@pytest.fixture
async def storage_repository(app) -> IStorageRepository:
    return app.container.services.storage()