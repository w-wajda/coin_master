from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.queries.companies.get_company import GetCompanyQuery
from app.application.queries.companies.get_company_list import GetCompanyListQuery
from app.application.queries.email_templates.get_email_template import GetEmailTemplateQuery
from app.application.queries.email_templates.get_email_template_list import GetEmailTemplateListQuery
from app.application.queries.tags.get_tag import GetTagQuery
from app.application.queries.tags.get_tag_list import GetTagListQuery
from app.application.queries.tokens.get_token import GetTokenQuery
from app.application.queries.tokens.get_token_list import GetTokenListQuery
from app.application.queries.users.get_user import GetUserQuery


class QueryContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    get_user: Provider[GetUserQuery] = providers.Callable(
        GetUserQuery,
        user_repository=repositories.user_repository,
    )

    get_token: Provider[GetTokenQuery] = providers.Callable(
        GetTokenQuery,
        token_repository=repositories.token_repository,
    )

    get_token_list: Provider[GetTokenListQuery] = providers.Callable(
        GetTokenListQuery,
        token_repository=repositories.token_repository,
        user_repository=repositories.user_repository,
    )

    get_email_template: Provider[GetEmailTemplateQuery] = providers.Callable(
        GetEmailTemplateQuery,
        email_template_repository=repositories.email_template_repository,
    )

    get_email_template_list: Provider[GetEmailTemplateListQuery] = providers.Callable(
        GetEmailTemplateListQuery,
        email_template_repository=repositories.email_template_repository,
    )

    get_company: Provider[GetCompanyQuery] = providers.Callable(
        GetCompanyQuery, company_repository=repositories.company_repository
    )

    get_company_list: Provider[GetCompanyListQuery] = providers.Callable(
        GetCompanyListQuery, company_repository=repositories.company_repository
    )

    get_tag: Provider[GetTagQuery] = providers.Callable(
        GetTagQuery, tag_repository=repositories.tag_repository
    )

    get_tag_list: Provider[GetTagListQuery] = providers.Callable(
        GetTagListQuery, tag_repository=repositories.tag_repository
    )
