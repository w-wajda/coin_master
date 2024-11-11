from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.users.user_exceptions import InvalidOldPassword
from app.domain.users.user_repository import IUserRepository
from app.domain.users.user_schemas import ChangePasswordSchema


class ChangePasswordCommand:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: int, change_password_data: ChangePasswordSchema):
        async with self.user_repository.start_session():
            user = await self.user_repository.get(user_id)

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            if not user.check_password(change_password_data.old_password):
                raise InvalidOldPassword()

            user.set_password(change_password_data.password1)
            await self.user_repository.commit()
