from datetime import (
    datetime,
    timedelta,
    timezone,
)

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.users.email_token import EmailToken
from app.domain.users.email_token_repository import IEmailTokenRepository
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import ResetPasswordSchema


class CreateResetPasswordTokenCommand:
    def __init__(
        self,
        user_repository: IUserRepository,
        email_token_repository: IEmailTokenRepository,
    ):
        self.user_repository = user_repository
        self.email_token_repository = email_token_repository

    async def __call__(self, reset_password_data: ResetPasswordSchema):
        async with self.user_repository.start_session() as session:
            self.email_token_repository.use_session(session)

        user = await self.user_repository.get_by_email(reset_password_data.email)
        if not user:
            # The endpoint returns a 204 (No Content) status to avoid disclosing whether a user with the provided email
            # exists.
            # This is intentionally implemented for security reasons, to prevent revealing information about the
            # existence or non-existence of a user (protection against enumeration attacks).
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=None)

        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=14)
        email_token = EmailToken(user=user, expires_at=expires_at, type=EmailToken.TYPES.password_reset.value)

        self.email_token_repository.add(email_token)
        await self.email_token_repository.commit()
        return None
