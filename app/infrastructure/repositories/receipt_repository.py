from app.domain.receipts.receipt import Receipt
from app.domain.receipts.receipt_repository import IReceiptRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyReceiptRepository(IReceiptRepository, GenericSQLAlchemyRepository[Receipt]):
    model = Receipt