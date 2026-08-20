from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.application.commands.users.change_password_with_token import ChangePasswordWithTokenCommand
from app.domain.exceptions import HTTPException
from app.domain.users.user_schemas import ChangePasswordWithTokenSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_token_repository():
    repo = make_repository()
    repo.get_by_reset_password_token = AsyncMock()
    return repo


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def command(email_token_repository, user_repository):
    return ChangePasswordWithTokenCommand(
        email_token_repository=email_token_repository, user_repository=user_repository
    )


def _schema(token="abc123"):
    return ChangePasswordWithTokenSchema(token=token, password1="new123456", password2="new123456")


async def test_change_password_with_token_success(command, email_token_repository, user_repository):
    user = MagicMock()
    email_token = MagicMock(user=user, is_used=False)
    email_token_repository.get_by_reset_password_token.return_value = email_token

    await command(change_password_with_token_schema=_schema())

    email_token_repository.get_by_reset_password_token.assert_awaited_once_with("abc123")
    user.set_password.assert_called_once_with("new123456")
    user_repository.commit.assert_awaited_once()
    assert email_token.is_used is True
    email_token_repository.commit.assert_awaited_once()


async def test_change_password_with_token_invalid_token(command, email_token_repository, user_repository):
    email_token_repository.get_by_reset_password_token.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(change_password_with_token_schema=_schema(token="bad"))

    assert exc_info.value.status_code == 404
    user_repository.commit.assert_not_awaited()
    email_token_repository.commit.assert_not_awaited()
