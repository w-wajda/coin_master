from abc import abstractmethod
from typing import Optional

from app.domain.common.repository import IBaseRepository
from app.domain.tokens.token import Token
from app.domain.users.user import User


class ITokenRepository(IBaseRepository[Token]):
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Token]:
        pass

    @abstractmethod
    async def get_for_user(self, user: User) -> Optional[Token]:
        pass
