from unittest.mock import MagicMock

import pytest

from app.application.queries.users.get_user import GetUserQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def query(user_repository):
    return GetUserQuery(user_repository=user_repository)


async def test_get_user_success(query, user_repository):
    user = MagicMock()
    user_repository.get.return_value = user

    result = await query(user_id=1)

    assert result is user


async def test_get_user_not_found(query, user_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1)

    assert exc_info.value.status_code == 404
