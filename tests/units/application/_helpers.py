from contextlib import asynccontextmanager
from unittest.mock import (
    AsyncMock,
    MagicMock,
)


def make_repository() -> MagicMock:
    """Repozytorium z podstawionymi metodami async, gotowe do wstrzyknięcia do komendy/zapytania."""
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.get_by = AsyncMock()
    repo.get_list = AsyncMock()
    repo.count = AsyncMock()
    repo.commit = AsyncMock()
    repo.delete = AsyncMock()
    repo.refresh = AsyncMock()

    @asynccontextmanager
    async def start_session():
        yield MagicMock()

    repo.start_session = start_session
    return repo
