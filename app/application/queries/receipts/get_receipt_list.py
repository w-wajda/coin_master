from mypy.server.objgraph import Iterable
from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.receipts.receipt import Receipt
from app.domain.receipts.receipt_repository import IReceiptRepository
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.conf import settings


class GetReceiptListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, user_repository: IUserRepository, receipt_repository: IReceiptRepository):
        self.user_repository = user_repository
        self.receipt_repository = receipt_repository

    async def __call__(self, user_id: int, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Receipt]:
        async with self.user_repository.start_session() as session:
            self.receipt_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            return await self.receipt_repository.get_list(user_id=user_id, limit=limit, offset=offset)
