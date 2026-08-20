from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.application.commands.tokens.create_token import CreateTokenCommand
from app.domain.users.user_exceptions import InvalidUserCredentials
from app.domain.users.user_schemas import UserLoginSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    repo = make_repository()
    repo.get_by_email = AsyncMock()
    return repo


@pytest.fixture
def token_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, token_repository):
    return CreateTokenCommand(user_repository=user_repository, token_repository=token_repository)


async def test_create_token_success(command, user_repository, token_repository):
    user = MagicMock(id=7)
    user.check_password.return_value = True
    user_repository.get_by_email.return_value = user

    token = await command(UserLoginSchema(email="a@example.com", password="secret123"))

    assert token.user_id == 7
    token_repository.add.assert_called_once_with(token)
    token_repository.commit.assert_awaited_once()


async def test_create_token_user_not_found(command, user_repository, token_repository):
    user_repository.get_by_email.return_value = None

    with pytest.raises(InvalidUserCredentials):
        await command(UserLoginSchema(email="a@example.com", password="secret123"))

    token_repository.add.assert_not_called()


async def test_create_token_wrong_password(command, user_repository, token_repository):
    user = MagicMock()
    user.check_password.return_value = False
    user_repository.get_by_email.return_value = user

    with pytest.raises(InvalidUserCredentials):
        await command(UserLoginSchema(email="a@example.com", password="wrong"))

    token_repository.add.assert_not_called()
