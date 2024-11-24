from app.domain.tags.tag import Tag
from app.domain.tags.tag_repository import ITagRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyTagRepository(ITagRepository, GenericSQLAlchemyRepository[Tag]):
    model = Tag
