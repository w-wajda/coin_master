import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.tags.update_tag import UpdateTagCommand
from app.domain.exceptions import HTTPException
from app.domain.tags.tag_schemas import CreateTagSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def tag_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, tag_repository):
    return UpdateTagCommand(user_repository=user_repository, tag_repository=tag_repository)


async def test_update_tag_success(command, user_repository, tag_repository):
    user_repository.get.return_value = object()
    tag = MagicMock()
    tag_repository.get_by.return_value = tag

    tag_data = CreateTagSchema(name="Travel")
    result = await command(user_id=1, uuid=uuid.uuid4(), tag_data=tag_data)

    assert result is tag
    tag.update.assert_called_once_with(**tag_data.model_dump(exclude_unset=True))
    tag_repository.commit.assert_awaited_once()


async def test_update_tag_user_not_found(command, user_repository, tag_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), tag_data=CreateTagSchema(name="Travel"))

    assert exc_info.value.status_code == 404
    tag_repository.get_by.assert_not_awaited()


async def test_update_tag_not_found(command, user_repository, tag_repository):
    user_repository.get.return_value = object()
    tag_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), tag_data=CreateTagSchema(name="Travel"))

    assert exc_info.value.status_code == 404
    tag_repository.commit.assert_not_awaited()
