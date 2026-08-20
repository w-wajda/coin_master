import factory

from app.domain.tokens.token import Token
from app.domain.users.user_factory import UserFactory


class TokenFactory(factory.Factory):
    user = factory.SubFactory(UserFactory)
    is_active = True

    class Meta:
        model = Token


__all__ = ["UserFactory", "TokenFactory"]
