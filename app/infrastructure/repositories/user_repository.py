from contextlib import asynccontextmanager
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import select

from app.domain.users.user import User
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyUserRepository(IUserRepository, GenericSQLAlchemyRepository[User]):
    model = User

    async def get(self, pk: int):
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(self.model).where(self.model.id == pk)
        cursor = await self.session.execute(statement)
        return cursor.scalar()

    async def get_public_profile(self, user_uuid: str) -> Optional[User]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = (
            select(self.model).where(self.model.uuid == user_uuid)
            # exclude users who are not ready
            .filter(User.is_ready.is_(True))
        )

        cursor = await self.session.execute(statement)
        return cursor.scalar()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(User).where(sa.func.lower(User.email) == email.lower())

        cursor = await self.session.execute(statement)
        return cursor.scalar()

    @asynccontextmanager
    async def begin(self):
        yield self.session
