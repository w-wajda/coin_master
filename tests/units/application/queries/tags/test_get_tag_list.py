from unittest.mock import MagicMock

import pytest

from app.application.queries.tags.get_tag_list import GetTagListQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def tag_repository():
    return make_repository()


@pytest.fixture
def query(user_repository, tag_repository):
    return GetTagListQuery(user_repository=user_repository, tag_repository=tag_repository)


async def test_get_tag_list_success(query, user_repository, tag_repository):
    user_repository.get.return_value = object()
    tags = [MagicMock(), MagicMock()]
    tag_repository.get_list.return_value = tags

    result = await query(user_id=1, limit=10, offset=0)

    assert result is tags
    tag_repository.get_list.assert_awaited_once_with(user_id=1, limit=10, offset=0)


async def test_get_tag_list_user_not_found(query, user_repository, tag_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1)

    assert exc_info.value.status_code == 404
    tag_repository.get_list.assert_not_awaited()
