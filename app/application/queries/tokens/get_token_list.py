import asyncio
from typing import Iterable

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.tokens.token import Token
from app.domain.tokens.token_repository import ITokenRepository
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.conf import settings


class GetTokenListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, token_repository: ITokenRepository, user_repository: IUserRepository):
        self.token_repository = token_repository
        self.user_repository = user_repository

    async def __call__(self, user_id: int, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Token]:
        async with self.user_repository.start_session() as session:
            self.token_repository.use_session(session)

            user = await self.user_repository.get(user_id)

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            token_list = await self.token_repository.get_list(user=user, limit=limit, offset=offset)
            await asyncio.gather(*(token.resolve_geo_ip_fields() for token in token_list))
            return token_list
