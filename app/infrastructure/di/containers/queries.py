from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.queries.abuses.get_abuse import GetAbuseQuery
from app.application.queries.abuses.get_abuse_list import GetAbuseListQuery
from app.application.queries.chats.get_chat_list import GetChatListQuery
from app.application.queries.chats.get_chat_message_list import GetChatMessageListQuery
from app.application.queries.email_templates.get_email_template import GetEmailTemplateQuery
from app.application.queries.email_templates.get_email_template_list import GetEmailTemplateListQuery
from app.application.queries.photos.get_photo import GetPhotoQuery
from app.application.queries.photos.get_photo_list import GetPhotoListQuery
from app.application.queries.tokens.get_token import GetTokenQuery
from app.application.queries.tokens.get_token_list import GetTokenListQuery
from app.application.queries.users.get_matches import GetMatchesQuery
from app.application.queries.users.get_next_girl import GetNextGirlQuery
from app.application.queries.users.get_public_profile import GetPublicProfileQuery
from app.application.queries.users.get_settings_query import GetSettingsQuery
from app.application.queries.users.get_user import GetUserQuery
from app.application.queries.votes.get_votes_list import GetVotesListQuery


class QueryContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    get_next_girl: Provider[GetNextGirlQuery] = providers.Callable(
        GetNextGirlQuery,
        user_repository=repositories.user_repository,
    )

    get_abuse: Provider[GetAbuseQuery] = providers.Callable(
        GetAbuseQuery,
        abuse_repository=repositories.abuse_repository,
        user_repository=repositories.user_repository,
    )

    get_email_template: Provider[GetEmailTemplateQuery] = providers.Callable(
        GetEmailTemplateQuery,
        email_template_repository=repositories.email_template_repository,
    )

    get_abuse_list: Provider[GetAbuseListQuery] = providers.Callable(
        GetAbuseListQuery,
        abuse_repository=repositories.abuse_repository,
        user_repository=repositories.user_repository,
    )

    get_email_template_list: Provider[GetEmailTemplateListQuery] = providers.Callable(
        GetEmailTemplateListQuery,
        email_template_repository=repositories.email_template_repository,
    )

    get_token: Provider[GetTokenQuery] = providers.Callable(
        GetTokenQuery,
        token_repository=repositories.token_repository,
    )

    get_chat_list: Provider[GetChatListQuery] = providers.Callable(
        GetChatListQuery,
        chat_repository=repositories.chat_repository,
        user_repository=repositories.user_repository,
    )

    get_chat_message_list: Provider[GetChatMessageListQuery] = providers.Callable(
        GetChatMessageListQuery,
        chat_repository=repositories.chat_repository,
        chat_message_repository=repositories.chat_message_repository,
        user_repository=repositories.user_repository,
    )
    get_votes_list: Provider[GetVotesListQuery] = providers.Callable(
        GetVotesListQuery,
        vote_repository=repositories.vote_repository,
        user_repository=repositories.user_repository,
    )

    get_photo: Provider[GetPhotoQuery] = providers.Callable(
        GetPhotoQuery,
        photo_repository=repositories.photo_repository,
        user_repository=repositories.user_repository,
    )

    get_photo_list: Provider[GetPhotoListQuery] = providers.Callable(
        GetPhotoListQuery,
        photo_repository=repositories.photo_repository,
        user_repository=repositories.user_repository,
    )

    get_matches: Provider[GetMatchesQuery] = providers.Callable(
        GetMatchesQuery,
        match_repository=repositories.match_repository,
        user_repository=repositories.user_repository,
    )

    get_token_list: Provider[GetTokenListQuery] = providers.Callable(
        GetTokenListQuery,
        token_repository=repositories.token_repository,
        user_repository=repositories.user_repository,
    )

    get_settings: Provider[GetSettingsQuery] = providers.Callable(
        GetSettingsQuery,
        user_repository=repositories.user_repository,
    )

    get_user: Provider[GetUserQuery] = providers.Callable(
        GetUserQuery,
        user_repository=repositories.user_repository,
    )

    get_public_profile_query: Provider[GetPublicProfileQuery] = providers.Callable(
        GetPublicProfileQuery,
        user_repository=repositories.user_repository,
    )