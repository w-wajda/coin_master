from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider
from sqlalchemy.ext.asyncio import AsyncSession


from app.infrastructure.repositories.token_repository import SQLAlchemyTokenRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

class RepositoryContainer(containers.DeclarativeContainer):
    session: Provider[AsyncSession] = providers.Dependency()

    user_repository: Provider[SQLAlchemyUserRepository] = providers.Callable(
        SQLAlchemyUserRepository,
        session=session,
    )

    token_repository: Provider[SQLAlchemyTokenRepository] = providers.Callable(
        SQLAlchemyTokenRepository,
        session=session,
    )
