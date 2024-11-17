import logging

from app.domain.users.user import User
from app.domain.users.user_exceptions import EmailAlreadyRegistered
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import UserCreateSchema


logger = logging.getLogger(__name__)


class CreateUserCommand:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_data: UserCreateSchema) -> User:
        logger.info(f"Creating a new user: {user_data}")

        async with self.user_repository.start_session():
            if await self.user_repository.get_by_email(user_data.email):
                raise EmailAlreadyRegistered(email=user_data.email)

            user = User(**user_data.model_dump(exclude={"password"}))
            user.set_password(user_data.password)

            self.user_repository.add(user)
            await self.user_repository.commit()

            logger.info(f"User created successfully: {user}")
            return user
