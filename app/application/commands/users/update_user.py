import logging

from app.domain.users.user import User
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import UserUpdateSchema


logger = logging.getLogger(__name__)


class UpdateUserCommand:
    """
    Update a user by current authenticated user. User can update her profile.
    """

    def __init__(self, user_repository: IUserRepository):
        logger.info(f"Initialized {self.__class__.__name__}")
        self.user_repository = user_repository

    async def __call__(self, user_id: int, user_data: UserUpdateSchema) -> User:
        logger.info(f"Update user: {user_id}, session_id: {id(self.user_repository.get_session())}")

        async with self.user_repository.start_session():
            user = await self.user_repository.get(user_id)

            if not user:
                raise ValueError("User not found")

            user.update(**user_data.model_dump(exclude_unset=True))


            await self.user_repository.commit()
            return user
