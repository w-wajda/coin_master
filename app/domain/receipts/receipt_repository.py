from abc import ABC

from app.domain.common.repository import IBaseRepository
from app.domain.receipts.receipt import Receipt


class IReceiptRepository(IBaseRepository[Receipt], ABC):
    pass
