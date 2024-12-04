import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    relationship,
)
from sqlalchemy.testing.schema import mapped_column

from app.domain.common.base import Base
from app.domain.receipts.receipt import Receipt
from app.domain.tags.tag import Tag


class ReceiptTag(Base):
    __tablename__ = "receipt_tags"

    tag_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("tags.id"))
    tag: Mapped[Tag] = relationship(backref="receipt_tags", foreign_keys="ReceiptTag.tag_id")

    receipt_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("receipts.id"))
    receipt: Mapped[Receipt] = relationship(backref="receipt_tags", foreign_keys="ReceiptTag.receipt_id")
