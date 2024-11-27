import logging

from dependency_injector.wiring import (
    Closing,
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status
from starlette.requests import Request

from app.application.commands.tokens.create_token import CreateTokenCommand
from app.application.commands.users.change_password import ChangePasswordCommand
from app.application.commands.users.change_password_with_token import ChangePasswordWithTokenCommand
from app.application.commands.users.create_reset_password_token import CreateResetPasswordTokenCommand
from app.application.commands.users.create_user import CreateUserCommand
from app.application.commands.users.update_user import UpdateUserCommand
from app.application.queries.users.get_user import GetUserQuery
from app.domain.tokens.token_schemas import TokenCreateSchema
from app.domain.users.user_exceptions import (
    EmailAlreadyRegistered,
    InvalidOldPassword,
)
from app.domain.users.user_schemas import (
    ChangePasswordSchema,
    ChangePasswordWithTokenSchema,
    ResetPasswordSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserSchema,
    UserUpdateSchema,
)
from app.infrastructure.decorators import (
    handle_exceptions,
    requires_auth,
)
from app.infrastructure.di import AppContainer


logger = logging.getLogger(__name__)

routes = APIRouter()


@routes.get("/{uuid/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_user(
    request: Request,
    get_user_query: GetUserQuery = Depends(Closing(Provide[AppContainer.queries.get_user])),  # noqa: B008
) -> UserSchema:
    """Get the authenticated user (current user details)"""
    user = await get_user_query(user_id=request.user.id)
    return UserSchema.model_validate(user)


@routes.get("/list/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_user_list():
    pass


@routes.post("/", status_code=status.HTTP_201_CREATED, tags=["Anonymous"])
@handle_exceptions(EmailAlreadyRegistered)
@inject
async def create_user(
    user_data: UserCreateSchema,
    create_user_command: CreateUserCommand = Depends(Provide[AppContainer.commands.create_user]),
    create_token_command: CreateTokenCommand = Depends(Provide[AppContainer.commands.create_token]),
) -> TokenCreateSchema:
    """Create a new user (register)"""
    await create_user_command(user_data=user_data)

    # Login the user after sign up
    user_login_data = UserLoginSchema(email=user_data.email, password=user_data.password)
    token = await create_token_command(user_login_data)

    return TokenCreateSchema.model_validate(token)


@routes.patch("/{uuid}/", tags=["Authenticated"])
@requires_auth()
@inject
async def patch_user(
    request: Request,
    user_data: UserUpdateSchema,
    update_user_command: UpdateUserCommand = Depends(Provide[AppContainer.commands.update_user]),
) -> UserSchema:
    """Update the authenticated user (update user details)"""
    user = await update_user_command(user_id=request.user.id, user_data=user_data)
    return UserSchema.model_validate(user)


@routes.get("/{uuid}/", tags=["Authenticated"])
@requires_auth()
@inject
async def delete_user():
    pass


@routes.post("/change-password/", tags=["Authenticated"], status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions(InvalidOldPassword)
@requires_auth()
@inject
async def change_password(
    request: Request,
    change_password_data: ChangePasswordSchema,
    change_password_command: ChangePasswordCommand = Depends(Provide[AppContainer.commands.change_password]),
):
    """Change the authenticated user's password"""
    await change_password_command(user_id=request.user.id, change_password_data=change_password_data)


@routes.post("/reset-password/", tags=["Anonymous"], status_code=status.HTTP_204_NO_CONTENT)
@inject
async def create_reset_password_token(
    reset_password_data: ResetPasswordSchema,
    reset_password_command: CreateResetPasswordTokenCommand = Depends(
        Provide[AppContainer.commands.create_reset_password_token]
    ),
):
    await reset_password_command(reset_password_data=reset_password_data)


@routes.post("/reset-password/confirm/", tags=["Anonymous"], status_code=status.HTTP_204_NO_CONTENT)
@inject
async def reset_password_confirm(
    change_password_with_token_schema: ChangePasswordWithTokenSchema,
    change_password_with_token_command: ChangePasswordWithTokenCommand = Depends(
        Provide[AppContainer.commands.change_password_with_token]
    ),
):
    await change_password_with_token_command(change_password_with_token_schema=change_password_with_token_schema)
