from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.domain.common.base import Base
from app.domain.users.user import User


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(backref="tags", foreign_keys="Tag.user_id")

