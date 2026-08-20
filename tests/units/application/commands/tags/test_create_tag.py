import pytest

from app.application.commands.tags.create_tag import CreateTagCommand
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
    return CreateTagCommand(user_repository=user_repository, tag_repository=tag_repository)


async def test_create_tag_success(command, user_repository, tag_repository):
    user_repository.get.return_value = object()

    tag = await command(user_id=1, tag_data=CreateTagSchema(name="Groceries"))

    assert tag.user_id == 1
    tag_repository.add.assert_called_once_with(tag)
    tag_repository.commit.assert_awaited_once()


async def test_create_tag_user_not_found(command, user_repository, tag_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, tag_data=CreateTagSchema(name="Groceries"))

    assert exc_info.value.status_code == 404
    tag_repository.add.assert_not_called()
