from uuid import UUID

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.receipts.receipt import Receipt
from app.domain.receipts.receipt_repository import IReceiptRepository
from app.domain.receipts.receipt_schemas import CreateReceiptSchema
from app.domain.users.user_repository import IUserRepository


class UpdateReceiptCommand:
    def __init__(self, user_repository: IUserRepository, receipt_repository: IReceiptRepository):
        self.user_repository = user_repository
        self.receipt_repository = receipt_repository

    async def __call__(self, user_id: int, uuid: UUID, receipt_data: CreateReceiptSchema) -> Receipt:
        async with self.user_repository.start_session() as session:
            self.receipt_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            if receipt := await self.receipt_repository.get_by(user_id=user_id, uuid=uuid):
                receipt.update(**receipt_data.model_dump(exclude_unset=True))
                await self.receipt_repository.commit()
                return receipt

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
