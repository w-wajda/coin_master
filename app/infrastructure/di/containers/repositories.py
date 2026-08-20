from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.company_repository import SQLAlchemyCompanyRepository
from app.infrastructure.repositories.email_template_repository import SQLAlchemyEmailTemplateRepository
from app.infrastructure.repositories.email_token_repository import SQLAlchemyEmailTokenRepository
from app.infrastructure.repositories.item_repository import SQLAlchemyItemRepository
from app.infrastructure.repositories.receipt_repository import SQLAlchemyReceiptRepository
from app.infrastructure.repositories.tag_repository import SQLAlchemyTagRepository
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

    company_repository: Provider[SQLAlchemyCompanyRepository] = providers.Callable(
        SQLAlchemyCompanyRepository,
        session=session,
    )

    receipt_repository: Provider[SQLAlchemyReceiptRepository] = providers.Callable(
        SQLAlchemyReceiptRepository,
        session=session,
    )

    item_repository: Provider[SQLAlchemyItemRepository] = providers.Callable(
        SQLAlchemyItemRepository,
        session=session,
    )

    tag_repository: Provider[SQLAlchemyTagRepository] = providers.Callable(
        SQLAlchemyTagRepository,
        session=session,
    )
