from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.application.services.send_email import SendEmailService
from app.infrastructure.conf import Settings
from app.infrastructure.storage.base import IStorageRepository
from app.infrastructure.storage.s3 import S3StorageRepository


class ServiceContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    config: Provider[Settings] = providers.Dependency()

    storage: Provider[IStorageRepository] = providers.Callable(S3StorageRepository, path="/")
    send_email_service: Provider[SendEmailService] = providers.Callable(
        SendEmailService,
        email_template_repository=repositories.email_template_repository,
        config=config,
    )
