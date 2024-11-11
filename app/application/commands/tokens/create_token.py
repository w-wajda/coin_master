import logging

from app.domain.tokens.token import Token
from app.domain.tokens.token_repository import ITokenRepository
from app.domain.users.user_exceptions import InvalidUserCredentials
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import (
    UserLoginSchema,
    UserRequestMeta,
)


logger = logging.getLogger(__name__)


class CreateTokenCommand:
    def __init__(self, user_repository: IUserRepository, token_repository: ITokenRepository):
        self.user_repository = user_repository
        self.token_repository = token_repository

    async def __call__(self, user_login_data: UserLoginSchema, user_request_meta: UserRequestMeta) -> Token:
        logger.info(f"Creating token for: {user_login_data.email=}")
        async with self.user_repository.start_session() as session:
            self.token_repository.use_session(session)

            user = await self.user_repository.get_by_email(user_login_data.email)

            if not user or not user.check_password(user_login_data.password):
                raise InvalidUserCredentials(email=user_login_data.email)

            token = Token(user=user, **user_request_meta.model_dump())
            self.token_repository.add(token)
            await self.token_repository.commit()

            logger.info(f"Token created successfully: {token}")
            return token
