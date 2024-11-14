from typing import Optional

from sqlalchemy import (
    func,
    select,
)

from app.domain.users.email_token import EmailToken
from app.domain.users.email_token_repository import IEmailTokenRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyEmailTokenRepository(IEmailTokenRepository, GenericSQLAlchemyRepository[EmailToken]):
    model = EmailToken

    async def get_by_reset_password_token(self, token: str) -> Optional[EmailToken]:
        if self.session is None:
            raise ValueError("Session is not initialized")

        statement = select(EmailToken).filter(
            EmailToken.token == token,
            EmailToken.is_used.is_(False),
            EmailToken.type == EmailToken.TYPES.password_reset.value,
            EmailToken.expires_at > func.now(),
        )
        result = await self.session.execute(statement)
        return result.scalar()
