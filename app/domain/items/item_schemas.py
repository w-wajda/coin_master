from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    price: Decimal


class CreateItemSchema(BaseModel):
    name: str
    price: Decimal
