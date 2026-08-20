from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.application.commands.users.create_reset_password_token import CreateResetPasswordTokenCommand
from app.domain.exceptions import HTTPException
from app.domain.users.email_token import EmailToken
from app.domain.users.user_schemas import ResetPasswordSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    repo = make_repository()
    repo.get_by_email = AsyncMock()
    return repo


@pytest.fixture
def email_token_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, email_token_repository):
    return CreateResetPasswordTokenCommand(
        user_repository=user_repository, email_token_repository=email_token_repository
    )


async def test_create_reset_password_token_success(command, user_repository, email_token_repository):
    user = MagicMock()
    user_repository.get_by_email.return_value = user

    result = await command(reset_password_data=ResetPasswordSchema(email="a@example.com"))

    assert result is None
    email_token_repository.add.assert_called_once()
    email_token_repository.commit.assert_awaited_once()

    added_token = email_token_repository.add.call_args[0][0]
    assert added_token.user is user
    assert added_token.type == EmailToken.TYPES.password_reset.value


async def test_create_reset_password_token_user_not_found(command, user_repository, email_token_repository):
    user_repository.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(reset_password_data=ResetPasswordSchema(email="a@example.com"))

    assert exc_info.value.status_code == 204
    email_token_repository.add.assert_not_called()
