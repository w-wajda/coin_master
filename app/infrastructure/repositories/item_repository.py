from app.domain.items.item import Item
from app.domain.items.item_repository import IItemRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyItemRepository(IItemRepository, GenericSQLAlchemyRepository[Item]):
    model = Item
