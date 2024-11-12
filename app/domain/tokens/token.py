import binascii
import os
from typing import Type

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.domain.common.base import Base
from app.domain.users.user import User


UserId = Type[int]


class Token(Base):
    __tablename__ = "tokens"

    token: Mapped[str] = mapped_column(sa.String(40), index=True)

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    user: Mapped[User] = relationship(lazy="joined", backref="tokens")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.token:
            self.token = binascii.hexlify(os.urandom(20)).decode()

    @property
    def scopes(self) -> list[str]:
        scopes = ["authenticated"]

        if self.user.is_staff:
            scopes.append("staff")

        return scopes
