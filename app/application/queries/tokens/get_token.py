import logging
from typing import Optional

from app.domain.tokens.token import Token
from app.domain.tokens.token_repository import ITokenRepository


logger = logging.getLogger(__name__)


class GetTokenQuery:
    def __init__(self, token_repository: ITokenRepository):
        self.token_repository = token_repository

    async def __call__(self, token: str) -> Optional[Token]:
        async with self.token_repository.start_session():
            return await self.token_repository.get_by_token(token)
