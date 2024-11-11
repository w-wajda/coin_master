import sqlalchemy as sa
from pwdlib import PasswordHash


from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domain.common.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(sa.String(254), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String(128))

    is_staff: Mapped[bool] = mapped_column(sa.Boolean(), default=False)

    def check_password(self, raw_password):
        password_hasher = PasswordHash.recommended()
        return password_hasher.verify(raw_password, self.password)

    def set_password(self, password):
        password_hasher = PasswordHash.recommended()
        self.password = password_hasher.hash(password)

    @property
    def is_authenticated(self) -> bool:
        return True

    def __str__(self):
        return f"{self.id}: {self.uuid}"
