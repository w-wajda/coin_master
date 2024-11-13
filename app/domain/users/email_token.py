import random
import string
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.domain.common.base import Base
from app.domain.users.user import User


class EmailToken(Base):
    __tablename__ = "email_tokens"

    token: Mapped[str] = mapped_column(sa.String(40), unique=True, nullable=False)

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(lazy="joined", backref="email_tokens")

    is_used: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    used_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = self.generate_token()

    @staticmethod
    def generate_token(length=40) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
