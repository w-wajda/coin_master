from abc import (
    ABC,
    abstractmethod,
)
from typing import Optional

from app.domain.common.repository import IBaseRepository
from app.domain.users.email_token import EmailToken


class IEmailTokenRepository(IBaseRepository[EmailToken], ABC):
    """Interface for email token repository"""

    @abstractmethod
    async def get_by_reset_password_token(self, token: str) -> Optional[EmailToken]:
        raise NotImplementedError
