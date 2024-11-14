
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.common.pubsub import IPubSub
from app.infrastructure.repositories.abuse_repository import SQLAlchemyAbuseRepository
from app.infrastructure.repositories.chat_message_repository import SQLAlchemyChatMessageRepository
from app.infrastructure.repositories.chat_repository import SQLAlchemyChatRepository
from app.infrastructure.repositories.email_template_repository import SQLAlchemyEmailTemplateRepository
from app.infrastructure.repositories.email_token_repository import SQLAlchemyEmailTokenRepository
from app.infrastructure.repositories.match_repository import SQLAlchemyMatchRepository
from app.infrastructure.repositories.photo_repository import SQLAlchemyPhotoRepository
from app.infrastructure.repositories.token_repository import SQLAlchemyTokenRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.vote_repository import SQLAlchemyVoteRepository


class RepositoryContainer(containers.DeclarativeContainer):
    session: Provider[AsyncSession] = providers.Dependency()
    pubsub: Provider[IPubSub] = providers.Dependency()

    user_repository: Provider[SQLAlchemyUserRepository] = providers.Callable(
        SQLAlchemyUserRepository,
        session=session,
    )

    chat_message_repository: Provider[SQLAlchemyChatMessageRepository] = providers.Callable(
        SQLAlchemyChatMessageRepository,
        session=session,
    )

    chat_repository: Provider[SQLAlchemyChatRepository] = providers.Callable(
        SQLAlchemyChatRepository,
        session=session,
    )

    email_token_repository: Provider[SQLAlchemyEmailTokenRepository] = providers.Callable(
        SQLAlchemyEmailTokenRepository,
        session=session,
    )

    abuse_repository: Provider[SQLAlchemyAbuseRepository] = providers.Callable(
        SQLAlchemyAbuseRepository,
        session=session,
    )

    token_repository: Provider[SQLAlchemyTokenRepository] = providers.Callable(
        SQLAlchemyTokenRepository,
        session=session,
    )

    vote_repository: Provider[SQLAlchemyVoteRepository] = providers.Callable(
        SQLAlchemyVoteRepository,
        session=session,
    )

    photo_repository: Provider[SQLAlchemyPhotoRepository] = providers.Callable(
        SQLAlchemyPhotoRepository,
        session=session,
    )

    match_repository: Provider[SQLAlchemyMatchRepository] = providers.Callable(
        SQLAlchemyMatchRepository,
        session=session,
    )

    email_template_repository: Provider[SQLAlchemyEmailTemplateRepository] = providers.Callable(
        SQLAlchemyEmailTemplateRepository,
        session=session,
    )