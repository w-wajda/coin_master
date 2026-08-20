import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.receipts.delete_receipt import DeleteReceiptCommand
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def receipt_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, receipt_repository):
    return DeleteReceiptCommand(user_repository=user_repository, receipt_repository=receipt_repository)


async def test_delete_receipt_success(command, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt = MagicMock()
    receipt_repository.get_by.return_value = receipt

    result = await command(user_id=1, uuid=uuid.uuid4())

    assert result is None
    receipt_repository.delete.assert_awaited_once_with(receipt)
    receipt_repository.commit.assert_awaited_once()


async def test_delete_receipt_user_not_found(command, user_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    receipt_repository.delete.assert_not_awaited()


async def test_delete_receipt_not_found(command, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    receipt_repository.delete.assert_not_awaited()
    receipt_repository.commit.assert_not_awaited()
