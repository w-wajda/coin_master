import abc
from typing import Optional

from app.domain.tokens.token import Token
from app.domain.users.user import User


class IAuthUser(abc.ABC):
    token: Optional[Token]
    user: Optional[User]


class IAuthUserWS(IAuthUser):
    pass
