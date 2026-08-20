import pytest

from app.infrastructure.repositories.token_repository import SQLAlchemyTokenRepository
from tests.factories import TokenFactory


@pytest.fixture
def repository(session_maker):
    return SQLAlchemyTokenRepository(session=session_maker)


async def test_get_by_token_returns_active_token(repository, user):
    async with repository.start_session() as session:
        token = TokenFactory(user=user)
        session.add(token)

    async with repository.start_session():
        found = await repository.get_by_token(token.token)
    assert found is not None
    assert found.id == token.id


async def test_get_by_token_ignores_inactive_token(repository, user):
    async with repository.start_session() as session:
        token = TokenFactory(user=user, is_active=False)
        session.add(token)

    async with repository.start_session():
        found = await repository.get_by_token(token.token)
    assert found is None


async def test_get_for_user_returns_token(repository, user):
    async with repository.start_session() as session:
        token = TokenFactory(user=user)
        session.add(token)

    async with repository.start_session():
        found = await repository.get_for_user(user)
    assert found.id == token.id


async def test_get_list_orders_newest_first(repository, user):
    async with repository.start_session() as session:
        first = TokenFactory(user=user)
        session.add(first)

    async with repository.start_session() as session:
        second = TokenFactory(user=user)
        session.add(second)

    async with repository.start_session():
        tokens = await repository.get_list(user_id=user.id)

    assert [token.id for token in tokens] == [second.id, first.id]


async def test_get_list_respects_limit(repository, user):
    async with repository.start_session() as session:
        for _ in range(3):
            session.add(TokenFactory(user=user))

    async with repository.start_session():
        tokens = await repository.get_list(user_id=user.id, limit=2)

    assert len(tokens) == 2
