from abc import ABC

from app.domain.common.repository import IBaseRepository
from app.domain.items.item import Item


class IItemRepository(IBaseRepository[Item], ABC):
    pass
