import logging
from typing import (
    Any,
    Callable,
    Optional,
    ParamSpec,
    Sequence,
)

from starlette import status
from starlette._utils import is_async_callable
from starlette.authentication import has_required_scope
from starlette.exceptions import HTTPException
from starlette.requests import (
    HTTPConnection,
    Request,
)

from .utils import fastapi_wraps


_P = ParamSpec("_P")

logger = logging.getLogger(__name__)


def _get_requires_http_async_handler(
    func: Callable[_P, Any],
    scopes_list: Optional[list[str]] = None,
):
    @fastapi_wraps(func)
    async def wrapper(
        *args: Any,
        __requestx: HTTPConnection,
        **kwargs: Any,
    ):
        # check if the user is authenticated
        if not __requestx.user.is_authenticated:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if scopes_list and not has_required_scope(__requestx, scopes_list):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return await func(*args, **kwargs)

    return wrapper


def _get_requires_http_sync_handler(
    func: Callable[_P, Any],
    scopes_list: Optional[list[str]] = None,
):
    @fastapi_wraps(func)
    def wrapper(
        *args: Any,
        __requestx: HTTPConnection,
        **kwargs: Any,
    ):
        # check if the user is authenticated
        if "authenticated" not in __requestx.auth.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # check if the user has the required scopes (permissions)
        if scopes_list and not has_required_scope(__requestx, scopes_list):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return func(*args, **kwargs)

    return wrapper


def requires_auth(
    scopes: Optional[str | Sequence[str]] = None,
) -> Callable[[Callable[_P, Any]], Callable[_P, Any]]:
    if scopes is None:
        scopes = []
    scopes_list = [scopes] if isinstance(scopes, str) else list(scopes)

    def decorator(
        func: Callable[_P, Any],
    ) -> Callable[_P, Any]:
        if is_async_callable(func):
            return _get_requires_http_async_handler(func, scopes_list)
        else:
            return _get_requires_http_sync_handler(func, scopes_list)

    return decorator


def requires_auth_dependency(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
