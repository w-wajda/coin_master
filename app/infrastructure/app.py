from typing import (
    Dict,
    List,
)

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
from starlette import status
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.infrastructure.di.app_container import init_di
from app.infrastructure.router import router as app_router
from app.version import __VERSION__


def initialize_app(di_container=None):
    app = FastAPI(title="Coin master API", version=__VERSION__)

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["coin-master.devsoft.pl", "localhost"])
    app.add_middleware(ProxyHeadersMiddleware)
    from app.infrastructure.auth import DefaultAuthenticationBackend
    from app.infrastructure.conf import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://coin-master.devsoft.pl"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )
    app.add_middleware(AuthenticationMiddleware, backend=DefaultAuthenticationBackend())

    app.container = di_container if di_container else init_di()

    app.include_router(app_router)

    if settings.RUN_ENV == "production":
        configure_sentry()

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors: Dict[str, List[str]] = {}

        for error in exc.errors():
            field = error["loc"][-1]
            message = error["msg"]

            if field not in errors:
                errors[field] = []

            errors[field].append(message)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
                "title": "One or more validation errors occurred.",
                "status": status.HTTP_400_BAD_REQUEST,
                "errors": errors,
            },
        )

    return app


def configure_sentry():
    import sentry_sdk
    from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        integrations=[
            StarletteIntegration(
                transaction_style="url",
                failed_request_status_codes=[403, range(500, 599)],
            ),
            FastApiIntegration(
                transaction_style="url",
                failed_request_status_codes=[403, range(500, 599)],
            ),
            SqlalchemyIntegration(),
            AsyncPGIntegration(),
        ]
    )
