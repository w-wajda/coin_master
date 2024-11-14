from typing import (
    Any,
    Optional,
    Sequence,
)

from sqlalchemy.future import select

from app.domain.tokens.token import Token
from app.domain.tokens.token_repository import ITokenRepository
from app.domain.users.user import User
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyTokenRepository(ITokenRepository, GenericSQLAlchemyRepository[Token]):
    model = Token

    async def get_by_token(self, token: str) -> Optional[Token]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(Token).filter(Token.token == token, Token.is_active.is_(True))
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_for_user(self, user: User) -> Optional[Token]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        result = await self.session.execute(select(Token).filter(Token.user_id == user.id))
        return result.scalar()

    async def get_list(self, limit=None, offset=None, **kwargs: Any) -> Sequence[Token]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(self.model).filter_by(**kwargs)

        if limit:
            statement = statement.limit(limit)

        if offset:
            statement = statement.offset(offset)

        statement = statement.order_by(self.model.last_activity.desc())

        cursor = await self.session.execute(statement)
        return cursor.scalars().all()
