import logging

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.users.user import User
from app.domain.users.user_repository import IUserRepository


logger = logging.getLogger(__name__)


class GetUserQuery:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: int) -> User:
        async with self.user_repository.start_session():
            logger.info(f"GetUserQuery.__call__: {user_id=}, session_id: {id(self.user_repository.get_session())}")
            user = await self.user_repository.get(user_id)

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            return user
