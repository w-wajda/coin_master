from unittest.mock import AsyncMock

import pytest

from app.application.commands.users.create_user import CreateUserCommand
from app.domain.users.user_exceptions import EmailAlreadyRegistered
from app.domain.users.user_schemas import UserCreateSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    repo = make_repository()
    repo.get_by_email = AsyncMock()
    return repo


@pytest.fixture
def command(user_repository):
    return CreateUserCommand(user_repository=user_repository)


async def test_create_user_success(command, user_repository):
    user_repository.get_by_email.return_value = None

    user = await command(user_data=UserCreateSchema(email="new@example.com", password="password123"))

    assert user.email == "new@example.com"
    assert user.check_password("password123")
    user_repository.add.assert_called_once_with(user)
    user_repository.commit.assert_awaited_once()


async def test_create_user_email_already_registered(command, user_repository):
    user_repository.get_by_email.return_value = object()

    with pytest.raises(EmailAlreadyRegistered):
        await command(user_data=UserCreateSchema(email="new@example.com", password="password123"))

    user_repository.add.assert_not_called()
