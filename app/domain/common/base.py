from datetime import datetime
from uuid import (
    UUID,
    uuid4,
)

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeMeta,
    Mapped,
    mapped_column,
    registry,
)


mapper_registry = registry()


class DeclarativeBase(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(type_=sa.UUID(as_uuid=True))

    created: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if not self.uuid:
            self.uuid = uuid4()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
