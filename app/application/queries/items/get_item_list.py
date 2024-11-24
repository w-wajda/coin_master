from typing import Iterable

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.items.item import Item
from app.domain.items.item_repository import IItemRepository
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.conf import settings


class GetItemListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, user_repository: IUserRepository, item_repository: IItemRepository):
        self.user_repository = user_repository
        self.item_repository = item_repository

    async def __call__(self, user_id: int, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Item]:
        async with self.user_repository.start_session() as session:
            self.item_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            return await self.item_repository.get_list(user=user, limit=limit, offset=offset)
