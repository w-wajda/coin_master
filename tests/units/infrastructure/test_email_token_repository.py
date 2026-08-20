from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from app.domain.users.email_token import EmailToken
from app.infrastructure.repositories.email_token_repository import SQLAlchemyEmailTokenRepository


@pytest.fixture
def repository(session_maker):
    return SQLAlchemyEmailTokenRepository(session=session_maker)


def _token(user, **overrides):
    defaults = {
        "user": user,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=1),
        "type": EmailToken.TYPES.password_reset.value,
    }
    defaults.update(overrides)
    return EmailToken(**defaults)


async def test_get_by_reset_password_token_returns_valid_token(repository, user):
    async with repository.start_session() as session:
        token = _token(user)
        session.add(token)

    async with repository.start_session():
        found = await repository.get_by_reset_password_token(token.token)
    assert found is not None
    assert found.id == token.id


async def test_get_by_reset_password_token_ignores_used_token(repository, user):
    async with repository.start_session() as session:
        token = _token(user, is_used=True)
        session.add(token)

    async with repository.start_session():
        found = await repository.get_by_reset_password_token(token.token)
    assert found is None


async def test_get_by_reset_password_token_ignores_expired_token(repository, user):
    async with repository.start_session() as session:
        token = _token(user, expires_at=datetime.now(timezone.utc) - timedelta(days=1))
        session.add(token)

    async with repository.start_session():
        found = await repository.get_by_reset_password_token(token.token)
    assert found is None
