from unittest.mock import MagicMock

import pytest

from app.application.queries.tokens.get_token_list import GetTokenListQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def token_repository():
    return make_repository()


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def query(token_repository, user_repository):
    return GetTokenListQuery(token_repository=token_repository, user_repository=user_repository)


async def test_get_token_list_success(query, token_repository, user_repository):
    user_repository.get.return_value = object()
    tokens = [MagicMock(), MagicMock()]
    token_repository.get_list.return_value = tokens

    result = await query(user_id=1, limit=10, offset=0)

    assert result is tokens
    token_repository.get_list.assert_awaited_once_with(user_id=1, limit=10, offset=0)


async def test_get_token_list_user_not_found(query, token_repository, user_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1)

    assert exc_info.value.status_code == 404
    token_repository.get_list.assert_not_awaited()
