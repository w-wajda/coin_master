from unittest.mock import MagicMock

import pytest

from app.application.commands.tokens.delete_token import DeleteTokenCommand
from tests.units.application._helpers import make_repository


@pytest.fixture
def token_repository():
    return make_repository()


@pytest.fixture
def command(token_repository):
    return DeleteTokenCommand(token_repository=token_repository)


async def test_delete_token_success(command, token_repository):
    token = MagicMock()
    token_repository.get_by.return_value = token

    await command(user_id=1, uuid="abc")

    assert token.is_active is False
    token_repository.commit.assert_awaited_once()


async def test_delete_token_not_found(command, token_repository):
    token_repository.get_by.return_value = None

    await command(user_id=1, uuid="abc")

    token_repository.commit.assert_not_awaited()
