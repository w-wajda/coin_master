import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domain.common.base import Base


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    address: Mapped[str] = mapped_column(sa.String(255), nullable=True)
