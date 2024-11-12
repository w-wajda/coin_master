from abc import abstractmethod
from typing import Optional

from app.domain.common.repository import IBaseRepository
from app.domain.users.user import User


class IUserRepository(IBaseRepository[User]):
    """Interface for user repository"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
