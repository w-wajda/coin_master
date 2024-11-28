from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.commands.companies.create_company import CreateCompanyCommand
from app.application.commands.companies.delete_company import DeleteCompanyCommand
from app.application.commands.companies.update_company import UpdateCompanyCommand
from app.application.commands.email_templates.create_email_template import CreateEmailTemplateCommand
from app.application.commands.email_templates.delete_email_template import DeleteEmailTemplateCommand
from app.application.commands.email_templates.update_email_template import UpdateEmailTemplateCommand
from app.application.commands.items.create_item import CreateItemCommand
from app.application.commands.items.delete_item import DeleteItemCommand
from app.application.commands.items.update_item import UpdateItemCommand
from app.application.commands.receipts.create_receipt import CreateReceiptCommand
from app.application.commands.tags.create_tag import CreateTagCommand
from app.application.commands.tags.delete_tag import DeleteTagCommand
from app.application.commands.tags.update_tag import UpdateTagCommand
from app.application.commands.tokens.create_token import CreateTokenCommand
from app.application.commands.tokens.delete_token import DeleteTokenCommand
from app.application.commands.tokens.revoke_token import RevokeTokenCommand
from app.application.commands.users.change_password import ChangePasswordCommand
from app.application.commands.users.change_password_with_token import ChangePasswordWithTokenCommand
from app.application.commands.users.create_reset_password_token import CreateResetPasswordTokenCommand
from app.application.commands.users.create_user import CreateUserCommand
from app.application.commands.users.update_user import UpdateUserCommand


class CommandContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    create_user: Provider[CreateUserCommand] = providers.Callable(
        CreateUserCommand,
        user_repository=repositories.user_repository,
    )

    update_user: Provider[UpdateUserCommand] = providers.Callable(
        UpdateUserCommand,
        user_repository=repositories.user_repository,
    )

    change_password: Provider[ChangePasswordCommand] = providers.Callable(
        ChangePasswordCommand,
        user_repository=repositories.user_repository,
    )

    create_reset_password_token: Provider[CreateResetPasswordTokenCommand] = providers.Callable(
        CreateResetPasswordTokenCommand,
        user_repository=repositories.user_repository,
        email_token_repository=repositories.email_token_repository,
    )

    change_password_with_token: Provider[ChangePasswordWithTokenCommand] = providers.Callable(
        ChangePasswordWithTokenCommand,
        email_token_repository=repositories.email_token_repository,
        user_repository=repositories.user_repository,
    )

    create_token: Provider[CreateTokenCommand] = providers.Callable(
        CreateTokenCommand,
        token_repository=repositories.token_repository,
        user_repository=repositories.user_repository,
    )

    revoke_token: Provider[RevokeTokenCommand] = providers.Callable(
        RevokeTokenCommand,
        token_repository=repositories.token_repository,
    )

    delete_token: Provider[DeleteTokenCommand] = providers.Callable(
        DeleteTokenCommand,
        token_repository=repositories.token_repository,
    )

    create_email_template: Provider[CreateEmailTemplateCommand] = providers.Callable(
        CreateEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    update_email_template: Provider[UpdateEmailTemplateCommand] = providers.Callable(
        UpdateEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    delete_email_template: Provider[DeleteEmailTemplateCommand] = providers.Callable(
        DeleteEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    create_company: Provider[CreateCompanyCommand] = providers.Callable(
        CreateCompanyCommand,
        company_repository=repositories.company_repository,
    )

    update_company: Provider[UpdateCompanyCommand] = providers.Callable(
        UpdateCompanyCommand,
        company_repository=repositories.company_repository,
    )

    delete_company: Provider[DeleteCompanyCommand] = providers.Callable(
        DeleteCompanyCommand,
        company_repository=repositories.company_repository,
    )

    create_tag: Provider[CreateTagCommand] = providers.Callable(
        CreateTagCommand,
        tag_repository=repositories.tag_repository,
    )

    update_tag: Provider[UpdateTagCommand] = providers.Callable(
        UpdateTagCommand,
        tag_repository=repositories.tag_repository,
    )

    delete_tag: Provider[DeleteTagCommand] = providers.Callable(
        DeleteTagCommand,
        tag_repository=repositories.tag_repository,
    )

    create_item: Provider[CreateItemCommand] = providers.Callable(
        CreateItemCommand,
        item_repository=repositories.item_repository,
    )

    update_item: Provider[UpdateItemCommand] = providers.Callable(
        UpdateItemCommand,
        item_repository=repositories.item_repository,
    )

    delete_item: Provider[DeleteItemCommand] = providers.Callable(
        DeleteItemCommand,
        item_repository=repositories.item_repository,
    )

    create_receipt: Provider[CreateReceiptCommand] = providers.Callable(
        CreateReceiptCommand, receipt_repository=repositories.receipt_repository
    )
