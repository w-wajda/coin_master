import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.domain.common.base import Base
from app.domain.users.user import User


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    address: Mapped[str] = mapped_column(sa.String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(backref="companies", foreign_keys="Company.user_id")
