import pytest

from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


@pytest.fixture
def repository(session_maker):
    return SQLAlchemyUserRepository(session=session_maker)


async def test_get_by_email_is_case_insensitive(repository, user):
    async with repository.start_session():
        found = await repository.get_by_email(user.email.upper())
    assert found is not None
    assert found.id == user.id


async def test_get_by_email_returns_none_when_missing(repository, user):
    async with repository.start_session():
        found = await repository.get_by_email("nobody@example.com")
    assert found is None
