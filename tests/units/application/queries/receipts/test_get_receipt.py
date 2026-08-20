import uuid
from unittest.mock import MagicMock

import pytest

from app.application.queries.receipts.get_receipt import GetReceiptQuery
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
    return GetReceiptQuery(user_repository=user_repository, receipt_repository=receipt_repository)


async def test_get_receipt_success(query, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt = MagicMock()
    receipt_repository.get_by.return_value = receipt

    result = await query(user_id=1, uuid=uuid.uuid4())

    assert result is receipt


async def test_get_receipt_user_not_found(query, user_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    receipt_repository.get_by.assert_not_awaited()


async def test_get_receipt_not_found(query, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
