from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.queries.tokens.get_token import GetTokenQuery
from app.application.queries.users.get_user import GetUserQuery


class QueryContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    get_token: Provider[GetTokenQuery] = providers.Callable(
        GetTokenQuery,
        token_repository=repositories.token_repository,
    )

    get_user: Provider[GetUserQuery] = providers.Callable(
        GetUserQuery,
        user_repository=repositories.user_repository,
    )
