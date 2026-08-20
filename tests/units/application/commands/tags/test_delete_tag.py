import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.tags.delete_tag import DeleteTagCommand
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def tag_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, tag_repository):
    return DeleteTagCommand(user_repository=user_repository, tag_repository=tag_repository)


async def test_delete_tag_success(command, user_repository, tag_repository):
    user_repository.get.return_value = object()
    tag = MagicMock()
    tag_repository.get_by.return_value = tag

    result = await command(user_id=1, uuid=uuid.uuid4())

    assert result is None
    tag_repository.delete.assert_awaited_once_with(tag)
    tag_repository.commit.assert_awaited_once()


async def test_delete_tag_user_not_found(command, user_repository, tag_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    tag_repository.delete.assert_not_awaited()


async def test_delete_tag_not_found(command, user_repository, tag_repository):
    user_repository.get.return_value = object()
    tag_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    tag_repository.delete.assert_not_awaited()
    tag_repository.commit.assert_not_awaited()
