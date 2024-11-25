from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ReceiptSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    amount: Decimal
    scan_file: str


class CreateReceiptSchema(BaseModel):
    amount: Decimal
    scan_file: str
