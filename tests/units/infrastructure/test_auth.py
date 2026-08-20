from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.infrastructure.auth import DefaultAuthenticationBackend


def _request(headers=None, cookies=None):
    request = MagicMock()
    request.headers = headers or {}
    request.cookies = cookies or {}
    return request


@pytest.fixture
def backend():
    return DefaultAuthenticationBackend()


async def test_authenticate_no_token_returns_none(backend):
    get_token_query = AsyncMock()

    result = await backend.authenticate(_request(), get_token_query=get_token_query)

    assert result is None
    get_token_query.assert_not_awaited()


async def test_authenticate_token_from_cookie(backend):
    user = MagicMock(is_staff=False)
    token = MagicMock(user=user)
    get_token_query = AsyncMock(return_value=token)

    result = await backend.authenticate(_request(cookies={"token": "abc"}), get_token_query=get_token_query)

    assert result is not None
    scopes, returned_user = result
    assert returned_user is user
    assert scopes.scopes == []
    get_token_query.assert_awaited_once_with("abc")


async def test_authenticate_invalid_token_returns_none(backend):
    get_token_query = AsyncMock(return_value=None)

    result = await backend.authenticate(
        _request(headers={"Authorization": "Token bad"}), get_token_query=get_token_query
    )

    assert result is None


async def test_authenticate_staff_user_gets_is_staff_scope(backend):
    user = MagicMock(is_staff=True)
    token = MagicMock(user=user)
    get_token_query = AsyncMock(return_value=token)

    result = await backend.authenticate(
        _request(headers={"Authorization": "Token abc"}), get_token_query=get_token_query
    )

    scopes, returned_user = result
    assert "is_staff" in scopes.scopes
