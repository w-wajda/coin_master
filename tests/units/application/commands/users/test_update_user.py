from unittest.mock import MagicMock

import pytest

from app.application.commands.users.update_user import UpdateUserCommand
from app.domain.users.user_schemas import UserUpdateSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def command(user_repository):
    return UpdateUserCommand(user_repository=user_repository)


async def test_update_user_success(command, user_repository):
    user = MagicMock()
    user_repository.get.return_value = user

    user_data = UserUpdateSchema(email="changed@example.com")
    result = await command(user_id=1, user_data=user_data)

    assert result is user
    user.update.assert_called_once_with(**user_data.model_dump(exclude_unset=True))
    user_repository.commit.assert_awaited_once()


async def test_update_user_not_found(command, user_repository):
    user_repository.get.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        await command(user_id=1, user_data=UserUpdateSchema(email="changed@example.com"))

    user_repository.commit.assert_not_awaited()
