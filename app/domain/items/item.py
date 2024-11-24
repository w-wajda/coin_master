from decimal import Decimal

from sqlalchemy.orm import mapped_column, Mapped, relationship
import sqlalchemy as sa
from app.domain.common.base import Base
from app.domain.users.user import User


class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(backref="items", foreign_keys="Item.user_id")