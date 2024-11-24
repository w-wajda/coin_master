from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.items.item import Item
from app.domain.items.item_repository import IItemRepository
from app.domain.items.item_schemas import CreateItemSchema
from app.domain.users.user_repository import IUserRepository


class CreateItemCommand:
    def __init__(self, user_repository: IUserRepository, item_repository: IItemRepository):
        self.user_repository = user_repository
        self.item_repository = item_repository

    async def __call__(self, user_id: int, item_data: CreateItemSchema) -> Item:
        async with self.user_repository.start_session() as session:
            self.item_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            item = Item(**item_data.model_dump())
            item.user_id = user_id

            self.item_repository.add(item)
            await self.item_repository.commit()
            return item
