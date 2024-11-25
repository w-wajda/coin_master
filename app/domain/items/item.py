from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.domain.common.base import Base
from app.domain.receipts.receipt import Receipt


class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)

    receipt_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("receipts.id"))
    receipt: Mapped[Receipt] = relationship(backref="items", foreign_keys="Item.receipt_id")
