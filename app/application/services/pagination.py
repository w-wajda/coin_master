from typing import (
    Annotated,
    Any,
    Generic,
    Iterable,
    TypedDict,
    TypeVar,
)

from fastapi import Query
from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.infrastructure.conf import settings


PaginationItemType = TypeVar("PaginationItemType")


class PaginatedSchema(BaseModel, Generic[PaginationItemType]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    page: int
    limit: int
    items: Iterable[PaginationItemType]


class PaginatedItems(TypedDict, Generic[PaginationItemType]):
    page: int
    limit: int
    items: Iterable[PaginationItemType]


class PaginationService:
    def __init__(
        self,
        page: Annotated[int, Query(gt=0)] = 1,
        limit: Annotated[int, Query(gt=0, lt=100)] = settings.PAGINATION_DEFAULT_LIMIT,
    ):
        self.page = page
        self.limit = limit

    @property
    def offset(self):
        return (self.page - 1) * self.limit

    def get_items(self, items: Iterable[Any]) -> PaginatedSchema:
        return PaginatedSchema(items=items, page=self.page, limit=self.limit)
