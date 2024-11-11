from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider
from app.application.commands.users.create_user import CreateUserCommand



class CommandContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    create_user: Provider[CreateUserCommand] = providers.Callable(
        CreateUserCommand,
        user_repository=repositories.user_repository,
    )
