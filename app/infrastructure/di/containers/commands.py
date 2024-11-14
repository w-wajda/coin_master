from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.commands.abuses.create_abuse import CreateAbuseCommand
from app.application.commands.abuses.delete_abuse import DeleteAbuseCommand
from app.application.commands.abuses.update_abuse import UpdateAbuseCommand
from app.application.commands.chats.create_message import CreateChatMessageCommand
from app.application.commands.email_templates.create_email_template import CreateEmailTemplateCommand
from app.application.commands.email_templates.delete_email_template import DeleteEmailTemplateCommand
from app.application.commands.email_templates.update_email_template import UpdateEmailTemplateCommand
from app.application.commands.photos.create_photo import CreatePhotoCommand
from app.application.commands.photos.create_photo_thumbnails import CreatePhotoThumbnailsCommand
from app.application.commands.photos.crop_image import CropImageCommand
from app.application.commands.photos.delete_photo import DeletePhotoCommand
from app.application.commands.photos.update_photo import UpdatePhotoCommand
from app.application.commands.photos.verify_upload_file_size import VerifyUploadFileSizeCommand
from app.application.commands.tokens.create_token import CreateTokenCommand
from app.application.commands.tokens.delete_token import DeleteTokenCommand
from app.application.commands.tokens.revoke_token import RevokeTokenCommand
from app.application.commands.users.change_password import ChangePasswordCommand
from app.application.commands.users.change_password_with_token import ChangePasswordWithTokenCommand
from app.application.commands.users.create_reset_password_token import CreateResetPasswordTokenCommand
from app.application.commands.users.create_user import CreateUserCommand
from app.application.commands.users.update_settings import UpdateSettingsCommand
from app.application.commands.users.update_user import UpdateUserCommand
from app.application.commands.votes.vote_user import VoteUserCommand
from app.domain.common.pubsub import IPubSub


class CommandContainer(containers.DeclarativeContainer):
    pubsub: Provider[IPubSub] = providers.Dependency()
    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    create_chat_message_command: Provider[CreateChatMessageCommand] = providers.Callable(
        CreateChatMessageCommand,
        pubsub=pubsub,
        user_repository=repositories.user_repository,
        chat_message_repository=repositories.chat_message_repository,
        chat_repository=repositories.chat_repository,
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

    create_abuse: Provider[CreateAbuseCommand] = providers.Callable(
        CreateAbuseCommand,
        abuse_repository=repositories.abuse_repository,
        user_repository=repositories.user_repository,
    )

    create_email_template: Provider[CreateEmailTemplateCommand] = providers.Callable(
        CreateEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    update_abuse: Provider[UpdateAbuseCommand] = providers.Callable(
        UpdateAbuseCommand,
        abuse_repository=repositories.abuse_repository,
    )

    update_email_template: Provider[UpdateEmailTemplateCommand] = providers.Callable(
        UpdateEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    delete_abuse: Provider[DeleteAbuseCommand] = providers.Callable(
        DeleteAbuseCommand,
        abuse_repository=repositories.abuse_repository,
    )

    delete_email_template: Provider[DeleteEmailTemplateCommand] = providers.Callable(
        DeleteEmailTemplateCommand,
        email_template_repository=repositories.email_template_repository,
    )

    delete_photo: Provider[DeletePhotoCommand] = providers.Callable(
        DeletePhotoCommand,
        photo_repository=repositories.photo_repository,
        user_repository=repositories.user_repository,
    )

    update_photo: Provider[UpdatePhotoCommand] = providers.Callable(
        UpdatePhotoCommand,
        photo_repository=repositories.photo_repository,
        user_repository=repositories.user_repository,
    )

    create_photo_thumbnails: Provider[CreatePhotoThumbnailsCommand] = providers.Callable(
        CreatePhotoThumbnailsCommand,
        storage=services.storage,
        photo_repository=repositories.photo_repository,
        user_repository=repositories.user_repository,
    )

    verify_upload_file_size: Provider[VerifyUploadFileSizeCommand] = providers.Callable(
        VerifyUploadFileSizeCommand,
    )

    create_photo: Provider[CreatePhotoCommand] = providers.Callable(
        CreatePhotoCommand,
        photo_repository=repositories.photo_repository,
        storage=services.storage,
        user_repository=repositories.user_repository,
    )

    crop_image_command: Provider[CropImageCommand] = providers.Callable(
        CropImageCommand,
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

    update_settings: Provider[UpdateSettingsCommand] = providers.Callable(
        UpdateSettingsCommand,
        user_repository=repositories.user_repository,
    )

    vote_user: Provider[VoteUserCommand] = providers.Callable(
        VoteUserCommand,
        vote_repository=repositories.vote_repository,
        match_repository=repositories.match_repository,
        user_repository=repositories.user_repository,
    )