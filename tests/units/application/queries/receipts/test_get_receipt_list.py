from unittest.mock import MagicMock

import pytest

from app.application.queries.receipts.get_receipt_list import GetReceiptListQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def receipt_repository():
    return make_repository()


@pytest.fixture
def query(user_repository, receipt_repository):
    return GetReceiptListQuery(user_repository=user_repository, receipt_repository=receipt_repository)


async def test_get_receipt_list_success(query, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipts = [MagicMock(), MagicMock()]
    receipt_repository.get_list.return_value = receipts

    result = await query(user_id=1, limit=10, offset=0)

    assert result is receipts
    receipt_repository.get_list.assert_awaited_once_with(user_id=1, limit=10, offset=0)


async def test_get_receipt_list_user_not_found(query, user_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1)

    assert exc_info.value.status_code == 404
    receipt_repository.get_list.assert_not_awaited()
