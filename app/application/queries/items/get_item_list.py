from typing import Iterable
from uuid import UUID

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.items.item import Item
from app.domain.items.item_repository import IItemRepository
from app.domain.receipts.receipt_repository import IReceiptRepository
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.conf import settings


class GetItemListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, user_repository: IUserRepository, item_repository: IItemRepository, receipt_repository: IReceiptRepository):
        self.user_repository = user_repository
        self.item_repository = item_repository
        self.receipt_repository = receipt_repository

    async def __call__(self, user_id: int, receipt_uuid: UUID, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Item]:
        async with self.user_repository.start_session() as session:
            self.item_repository.use_session(session)
            self.receipt_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            receipt = await self.receipt_repository.get_by(user_id=user.id, uuid=receipt_uuid)
            if not receipt:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")

            return await self.item_repository.get_list(user_id=user.id, receipt_id=receipt.id, limit=limit, offset=offset)
