from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Provider

from app.infrastructure.conf import (
    Settings,
    get_path,
)
from app.infrastructure.database import get_async_session
from app.infrastructure.di.containers.commands import CommandContainer
from app.infrastructure.di.containers.queries import QueryContainer
from app.infrastructure.di.containers.repositories import RepositoryContainer
from app.infrastructure.di.utils import generate_modules_list


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(auto_wire=True)

    config: Provider[Settings] = providers.Singleton(Settings, _env_file=get_path(".env"))

    session = providers.Factory(get_async_session)

    repositories = providers.Container(
        RepositoryContainer,
        session=session,
    )

    commands = providers.Container(
        CommandContainer,
        repositories=repositories,
    )

    queries = providers.Container(
        QueryContainer,
        repositories=repositories,
    )


def init_di():
    paths = [
        get_path("app/application/websockets/handlers"),
        get_path("app/presentation/endpoints"),
        get_path("app/presentation/cli"),
        get_path("app/infrastructure/auth"),
    ]

    container = AppContainer()
    container.wire(modules=generate_modules_list(paths, get_path(".")))
    return container