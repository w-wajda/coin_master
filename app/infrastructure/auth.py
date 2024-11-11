import logging
import os
from typing import (
    Optional,
    ParamSpec,
)

from dependency_injector.wiring import (
    Closing,
    Provide,
    inject,
)
from fastapi import Depends
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
)
from starlette.requests import HTTPConnection

from app.application.queries.tokens.get_token import GetTokenQuery
from app.infrastructure.di import AppContainer


_P = ParamSpec("_P")

logger = logging.getLogger(__name__)


class DefaultAuthenticationBackend(AuthenticationBackend):
    """
    A default authentication backend that checks for a token in the Authorization header
    and in the cookies.

    If a token is found, it will be used to authenticate the user. If the user is found,
    the scopes will be set to ["authenticated"]. If the user is a staff member, the scopes
    will be set to ["authenticated", "is_staff"]. If the user is ready, the scopes will be
    set to ["authenticated", "is_ready"].
    """

    @inject
    async def authenticate(
        self,
        request: HTTPConnection,
        get_token_query: GetTokenQuery = Depends(Closing(Provide[AppContainer.queries.get_token])),  # noqa: B008
    ):

        # Try to get a token from Authorization header
        authorization = request.headers.get("Authorization")
        scheme, token_string = get_authorization_scheme_param(authorization)

        # Try to get a token from cookie
        if not token_string:
            token_string = request.cookies.get("token") or ""

        if not token_string:
            return None

        if token := await get_token_query(token_string):
            scopes = []
            user = token.user

            pid = os.getpid()
            logging.info(f"User object ID: {id(user)}, processed in thread {pid}, bio: {user.bio}")

            if user.is_staff:
                scopes.append("is_staff")
            return AuthCredentials(scopes), token.user

