from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Generic,
    Iterable,
    Optional,
    Sequence,
    TypeVar,
)

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class IBaseRepository(ABC, Generic[T]):

    @abstractmethod
    def add(self, instance: T) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def get(self, pk: int) -> Optional[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def get_by(self, **filters) -> Optional[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def delete(self, instance: T) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def get_list(self, limit=None, offset=None, **kwargs: Any) -> Iterable[T]:
        pass  # pragma: no cover

    @abstractmethod
    async def commit(self) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def refresh(self, instance: T) -> None:
        pass

    @abstractmethod
    async def all(self) -> Sequence[T]:
        pass

    @abstractmethod
    def expire(self, obj: T) -> int:
        pass

    @abstractmethod
    def get_session(self):
        pass

    @abstractmethod
    async def start_session(self):
        pass

    @abstractmethod
    def use_session(self, session: AsyncSession):
        pass