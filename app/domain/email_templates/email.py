import enum

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domain.common.base import Base


class EmailTypeEnum(enum.Enum):
    EMAIL_CONFIRMATION = "email_confirmation"
    WELCOME = "welcome"


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    email_type: Mapped[str] = mapped_column(sa.Enum(EmailTypeEnum), nullable=False)
    subject: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    text_content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    html_content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=False)
