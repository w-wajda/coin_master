from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.application.queries.tokens.get_token import GetTokenQuery
from tests.units.application._helpers import make_repository


@pytest.fixture
def token_repository():
    repo = make_repository()
    repo.get_by_token = AsyncMock()
    return repo


@pytest.fixture
def query(token_repository):
    return GetTokenQuery(token_repository=token_repository)


async def test_get_token_success(query, token_repository):
    token = MagicMock()
    token_repository.get_by_token.return_value = token

    result = await query(token="abc")

    assert result is token
    token_repository.get_by_token.assert_awaited_once_with("abc")


async def test_get_token_not_found(query, token_repository):
    token_repository.get_by_token.return_value = None

    result = await query(token="abc")

    assert result is None
