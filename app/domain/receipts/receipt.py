from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.common.base import Base
from app.domain.companies.company import Company
from app.domain.users.user import User


class Receipt(Base):
    __tablename__ = "receipts"

    amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    scan_file: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    company_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("companies.id"))
    company: Mapped[Company] = relationship(backref="receipts", foreign_keys="Receipt.company_id")

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(backref="receipts", foreign_keys="Receipt.user_id")
