from abc import ABC

from app.domain.common.repository import IBaseRepository
from app.domain.tags.tag import Tag


class ITagRepository(IBaseRepository[Tag], ABC):
    pass
