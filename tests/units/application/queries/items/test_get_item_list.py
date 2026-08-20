import uuid
from unittest.mock import MagicMock

import pytest

from app.application.queries.items.get_item_list import GetItemListQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def item_repository():
    return make_repository()


@pytest.fixture
def receipt_repository():
    return make_repository()


@pytest.fixture
def query(user_repository, item_repository, receipt_repository):
    return GetItemListQuery(
        user_repository=user_repository, item_repository=item_repository, receipt_repository=receipt_repository
    )


async def test_get_item_list_success(query, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = MagicMock(id=42)
    items = [MagicMock(), MagicMock()]
    item_repository.get_list.return_value = items

    result = await query(user_id=1, receipt_uuid=uuid.uuid4(), limit=10, offset=0)

    assert result is items
    item_repository.get_list.assert_awaited_once_with(receipt_id=42, limit=10, offset=0)


async def test_get_item_list_user_not_found(query, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, receipt_uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    receipt_repository.get_by.assert_not_awaited()


async def test_get_item_list_receipt_not_found(query, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, receipt_uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    item_repository.get_list.assert_not_awaited()
