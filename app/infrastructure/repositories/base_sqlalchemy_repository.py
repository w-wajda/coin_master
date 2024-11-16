import logging
from contextlib import asynccontextmanager
from typing import (
    Any,
    Generic,
    Optional,
    Sequence,
    TypeVar,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.common.repository import IBaseRepository


T = TypeVar("T")

logger = logging.getLogger(__name__)


class GenericSQLAlchemyRepository(IBaseRepository, Generic[T]):
    model: Any

    def __init__(self, session: AsyncSession) -> None:
        self.session_maker = session
        self.session: AsyncSession | None = None

    @asynccontextmanager
    async def start_session(self):
        async with self.session_maker() as session:
            session_id = id(session)
            logger.info(f"New SQLAlchemy session: {session_id=}")
            try:
                self.session = session
                yield session
                logger.info("Commit session, almost done.")
                await session.commit()
            except Exception as e:
                logger.error(f"Got error but session was not commited. Rollback: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
                logger.info(f"Closed session: {session_id}")

    def use_session(self, session: AsyncSession):
        self.session = session

    def get_session(self):
        return self.session

    def add(self, instance: T):
        if self.session is None:
            raise ValueError("Session is not initialized")

        self.session.add(instance)

    async def get(self, pk: int) -> Optional[T]:
        if self.session is None:
            raise ValueError("Session is not initialized")
        return await self.get_by(id=pk)

    async def get_by(self, **filters) -> Optional[T]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(self.model).filter_by(**filters)

        cursor = await self.session.execute(statement)
        return cursor.scalar()

    async def get_list(self, limit=None, offset=None, **kwargs: Any) -> Sequence[T]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(self.model).filter_by(**kwargs)

        if limit:
            statement = statement.limit(limit)

        if offset:
            statement = statement.offset(offset)

        cursor = await self.session.execute(statement)
        return cursor.scalars().all()

    async def commit(self) -> None:
        if self.session is None:
            raise ValueError("Session is not initialized")

        await self.session.commit()

    async def refresh(self, instance: T) -> None:
        if self.session is None:
            raise ValueError("Session is not initialized")

        await self.session.refresh(instance)

    async def all(self) -> Sequence[T]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    def expire(self, obj: T):
        if self.session is None:
            raise ValueError("Session is not initialized")

        self.session.expire(obj)

    async def delete(self, instance: T) -> None:
        if self.session is None:
            raise ValueError("Session is not initialized")

        await self.session.delete(instance)
