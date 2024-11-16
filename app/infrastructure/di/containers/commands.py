from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.commands.email_templates.create_email_template import CreateEmailTemplateCommand
from app.application.commands.email_templates.delete_email_template import DeleteEmailTemplateCommand
from app.application.commands.email_templates.update_email_template import UpdateEmailTemplateCommand
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

    change_password: Provider[ChangePasswordCommand] = providers.Callable(
        ChangePasswordCommand,
        user_repository=repositories.user_repository,
    )

    change_password_with_token: Provider[ChangePasswordWithTokenCommand] = providers.Callable(
        ChangePasswordWithTokenCommand,
        email_token_repository=repositories.email_token_repository,
        user_repository=repositories.user_repository,
    )

    create_reset_password_token: Provider[CreateResetPasswordTokenCommand] = providers.Callable(
        CreateResetPasswordTokenCommand,
        user_repository=repositories.user_repository,
        email_token_repository=repositories.email_token_repository,
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
