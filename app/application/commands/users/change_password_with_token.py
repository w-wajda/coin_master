from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.users.email_token_repository import IEmailTokenRepository
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import ChangePasswordWithTokenSchema


class ChangePasswordWithTokenCommand:
    def __init__(self, email_token_repository: IEmailTokenRepository, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.email_token_repository = email_token_repository

    async def __call__(self, change_password_with_token_schema: ChangePasswordWithTokenSchema):
        token = change_password_with_token_schema.token

        async with self.email_token_repository.start_session() as session:
            self.user_repository.use_session(session)

        email_token = await self.email_token_repository.get_by_reset_password_token(token)

        if not email_token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token is invalid or expired")

        user = email_token.user
        user.set_password(change_password_with_token_schema.password1)
        await self.user_repository.commit()

        email_token.is_used = True
        await self.email_token_repository.commit()
