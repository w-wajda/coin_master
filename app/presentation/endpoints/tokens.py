from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.security.utils import get_authorization_scheme_param
from starlette import status

from app.application.commands.tokens.create_token import CreateTokenCommand
from app.application.commands.tokens.delete_token import DeleteTokenCommand
from app.application.commands.tokens.revoke_token import RevokeTokenCommand
from app.application.queries.tokens.get_token_list import GetTokenListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.tokens.token_schemas import (
    TokenCreateSchema,
    TokenSchema,
)
from app.domain.users.user_exceptions import InvalidUserCredentials
from app.domain.users.user_schemas import UserLoginSchema
from app.infrastructure.decorators import (
    handle_exceptions,
    requires_auth,
)
from app.infrastructure.di import AppContainer

routes = APIRouter()


@routes.post("/create_token/", status_code=status.HTTP_201_CREATED, tags=["Anonymous"])
@handle_exceptions(InvalidUserCredentials)
@inject
async def create_token(
    user_login_data: UserLoginSchema,
    create_token_command: CreateTokenCommand = Depends(Provide[AppContainer.commands.create_token]),
) -> TokenCreateSchema:
    token = await create_token_command(user_login_data)
    return TokenCreateSchema.model_validate(token)


@routes.delete("/revoke_token/", status_code=status.HTTP_204_NO_CONTENT, tags=["Authenticated"])
@requires_auth()
@inject
async def revoke_token(
    request: Request,
    revoke_token_command: RevokeTokenCommand = Depends(Provide[AppContainer.commands.revoke_token]),
):
    authorization = request.headers.get("Authorization")
    _, token_string = get_authorization_scheme_param(authorization)

    if token_string:
        await revoke_token_command(token_string)


@routes.delete("/delete_token/{uuid}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Authenticated"])
@requires_auth()
@inject
async def delete_token(
    uuid: str,
    request: Request,
    delete_command_token: DeleteTokenCommand = Depends(Provide[AppContainer.commands.delete_token]),
):
    await delete_command_token(request.user.id, uuid)


@routes.get("/get_token_list/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_token_list(
    request: Request,
    get_token_list_query: GetTokenListQuery = Depends(Provide[AppContainer.queries.get_token_list]),
    pagination: PaginationService = Depends(),
) -> PaginatedSchema[TokenSchema]:
    tokens = await get_token_list_query(request.user.id, limit=pagination.limit, offset=pagination.offset)
    return pagination.get_items(tokens)