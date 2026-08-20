from unittest.mock import MagicMock

import pytest

from app.application.commands.users.change_password import ChangePasswordCommand
from app.domain.exceptions import HTTPException
from app.domain.users.user_exceptions import InvalidOldPassword
from app.domain.users.user_schemas import ChangePasswordSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def command(user_repository):
    return ChangePasswordCommand(user_repository=user_repository)


def _schema():
    return ChangePasswordSchema(old_password="old12345", password1="new123456", password2="new123456")


async def test_change_password_success(command, user_repository):
    user = MagicMock()
    user.check_password.return_value = True
    user_repository.get.return_value = user

    await command(user_id=1, change_password_data=_schema())

    user.check_password.assert_called_once_with("old12345")
    user.set_password.assert_called_once_with("new123456")
    user_repository.commit.assert_awaited_once()


async def test_change_password_user_not_found(command, user_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, change_password_data=_schema())

    assert exc_info.value.status_code == 404
    user_repository.commit.assert_not_awaited()


async def test_change_password_invalid_old_password(command, user_repository):
    user = MagicMock()
    user.check_password.return_value = False
    user_repository.get.return_value = user

    with pytest.raises(InvalidOldPassword):
        await command(user_id=1, change_password_data=_schema())

    user.set_password.assert_not_called()
    user_repository.commit.assert_not_awaited()
