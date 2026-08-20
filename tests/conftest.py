import asyncio

import pytest
import sqlalchemy as sa
from dependency_injector import providers
from httpx import (
    ASGITransport,
    AsyncClient,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

# WAŻNE: wszystkie modele muszą być zaimportowane, żeby Base.metadata je znała
import app.domain.companies.company  # noqa: F401
import app.domain.email_templates.email  # noqa: F401
import app.domain.items.item  # noqa: F401
import app.domain.receipt_tags.receipt_tag  # noqa: F401
import app.domain.receipts.receipt  # noqa: F401
import app.domain.tags.tag  # noqa: F401
import app.domain.tokens.token  # noqa: F401
import app.domain.users.email_token  # noqa: F401
import app.domain.users.user  # noqa: F401
from app.domain.common.base import Base
from app.infrastructure.app import initialize_app
from app.infrastructure.di.app_container import init_di
from app.infrastructure.storage.fake_s3 import FakeS3StorageRepository
from tests.factories import (
    CompanyFactory,
    ReceiptFactory,
    TokenFactory,
    UserFactory,
)


TEST_DB_HOST = "localhost"
TEST_DB_PORT = 5432
TEST_DB_NAME = "coins_test"
TEST_DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"


async def _ensure_test_database_exists() -> None:
    maintenance_engine = create_async_engine(
        f"postgresql+asyncpg://postgres:postgres@{TEST_DB_HOST}:{TEST_DB_PORT}/postgres",
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    async with maintenance_engine.connect() as conn:
        exists = await conn.scalar(sa.text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME})
        if not exists:
            await conn.execute(sa.text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    await maintenance_engine.dispose()


async def _reset_schema() -> None:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_database():
    """Osobna, jednorazowa pętla asyncio — celowo niezależna od pętli pytest-asyncio,
    żeby pula połączeń silnika testowego z fixture `engine` nigdy nie trafiła
    na połączenie otwarte na innej, już zamkniętej pętli."""
    asyncio.run(_ensure_test_database_exists())
    asyncio.run(_reset_schema())


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session_maker(engine):
    """Czyści dane po każdym teście — repozytoria same commitują i zamykają sesję
    (`GenericSQLAlchemyRepository.start_session`), więc zagnieżdżona transakcja
    z rollbackiem tu nie zadziała. TRUNCATE jest wolniejszy, ale przewidywalny."""
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    yield maker
    async with engine.begin() as conn:
        tables = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
        await conn.exec_driver_sql(f"TRUNCATE {tables} RESTART IDENTITY CASCADE")


@pytest.fixture
def storage():
    return FakeS3StorageRepository(path="/")


@pytest.fixture
def container(session_maker, storage):
    c = init_di()
    c.session.override(providers.Object(session_maker))
    c.services.storage.override(providers.Object(storage))
    yield c
    c.unwire()


@pytest.fixture
async def client(container):
    asgi_app = initialize_app(di_container=container)
    transport = ASGITransport(app=asgi_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


@pytest.fixture
async def user(session_maker):
    async with session_maker() as session:
        obj = UserFactory()
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj


@pytest.fixture
async def token(session_maker, user):
    async with session_maker() as session:
        obj = TokenFactory(user=user)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj


@pytest.fixture
async def authenticated_client(client, token):
    client.headers["Authorization"] = f"Token {token.token}"
    return client


@pytest.fixture
async def staff_user(session_maker):
    async with session_maker() as session:
        obj = UserFactory(is_staff=True)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj


@pytest.fixture
async def staff_token(session_maker, staff_user):
    async with session_maker() as session:
        obj = TokenFactory(user=staff_user)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj


@pytest.fixture
async def staff_client(client, staff_token):
    client.headers["Authorization"] = f"Token {staff_token.token}"
    return client


@pytest.fixture
async def company(session_maker, user):
    async with session_maker() as session:
        obj = CompanyFactory(user=user)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj


@pytest.fixture
async def receipt(session_maker, user, company):
    async with session_maker() as session:
        obj = ReceiptFactory(user=user, company=company)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj
