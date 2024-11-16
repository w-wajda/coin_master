
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.email_template_repository import SQLAlchemyEmailTemplateRepository
from app.infrastructure.repositories.email_token_repository import SQLAlchemyEmailTokenRepository
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

    email_token_repository: Provider[SQLAlchemyEmailTokenRepository] = providers.Callable(
        SQLAlchemyEmailTokenRepository,
        session=session,
    )

    email_template_repository: Provider[SQLAlchemyEmailTemplateRepository] = providers.Callable(
        SQLAlchemyEmailTemplateRepository,
        session=session,
    )