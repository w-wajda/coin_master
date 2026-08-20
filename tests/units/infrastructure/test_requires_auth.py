from types import SimpleNamespace

import pytest
from starlette.exceptions import HTTPException

from app.infrastructure.decorators.requires_auth import (
    requires_auth,
    requires_auth_dependency,
)


def _connection(*, authenticated: bool = True, scopes: list[str] | None = None):
    return SimpleNamespace(
        user=SimpleNamespace(is_authenticated=authenticated),
        auth=SimpleNamespace(scopes=scopes or []),
    )


async def test_requires_auth_async_allows_authenticated_call():
    @requires_auth()
    async def handler():
        return "ok"

    result = await handler(__requestx=_connection(authenticated=True))
    assert result == "ok"


async def test_requires_auth_async_unauthenticated_raises_401():
    @requires_auth()
    async def handler():
        return "ok"

    with pytest.raises(HTTPException) as exc_info:
        await handler(__requestx=_connection(authenticated=False))
    assert exc_info.value.status_code == 401


async def test_requires_auth_async_missing_scope_raises_403():
    @requires_auth(scopes="is_staff")
    async def handler():
        return "ok"

    with pytest.raises(HTTPException) as exc_info:
        await handler(__requestx=_connection(authenticated=True, scopes=["authenticated"]))
    assert exc_info.value.status_code == 403


async def test_requires_auth_async_with_required_scope_allows_call():
    @requires_auth(scopes="is_staff")
    async def handler():
        return "ok"

    result = await handler(__requestx=_connection(authenticated=True, scopes=["authenticated", "is_staff"]))
    assert result == "ok"


def test_requires_auth_sync_allows_authenticated_call():
    @requires_auth()
    def handler():
        return "ok"

    result = handler(__requestx=_connection(scopes=["authenticated"]))
    assert result == "ok"


def test_requires_auth_sync_unauthenticated_raises_401():
    @requires_auth()
    def handler():
        return "ok"

    with pytest.raises(HTTPException) as exc_info:
        handler(__requestx=_connection(scopes=[]))
    assert exc_info.value.status_code == 401


def test_requires_auth_sync_missing_scope_raises_403():
    @requires_auth(scopes="is_staff")
    def handler():
        return "ok"

    with pytest.raises(HTTPException) as exc_info:
        handler(__requestx=_connection(scopes=["authenticated"]))
    assert exc_info.value.status_code == 403


def test_requires_auth_dependency_authenticated_passes():
    assert requires_auth_dependency(_connection(authenticated=True)) is None


def test_requires_auth_dependency_unauthenticated_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        requires_auth_dependency(_connection(authenticated=False))
    assert exc_info.value.status_code == 401
