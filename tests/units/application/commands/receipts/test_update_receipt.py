import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.receipts.update_receipt import UpdateReceiptCommand
from app.domain.exceptions import HTTPException
from app.domain.receipts.receipt_schemas import CreateReceiptSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def receipt_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, receipt_repository):
    return UpdateReceiptCommand(user_repository=user_repository, receipt_repository=receipt_repository)


async def test_update_receipt_success(command, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt = MagicMock()
    receipt_repository.get_by.return_value = receipt

    receipt_data = CreateReceiptSchema(amount="12.00", scan_file="new.jpg")
    result = await command(user_id=1, uuid=uuid.uuid4(), receipt_data=receipt_data)

    assert result is receipt
    receipt.update.assert_called_once_with(**receipt_data.model_dump(exclude_unset=True))
    receipt_repository.commit.assert_awaited_once()


async def test_update_receipt_user_not_found(command, user_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), receipt_data=CreateReceiptSchema(amount="1", scan_file="a.jpg"))

    assert exc_info.value.status_code == 404
    receipt_repository.get_by.assert_not_awaited()


async def test_update_receipt_not_found(command, user_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), receipt_data=CreateReceiptSchema(amount="1", scan_file="a.jpg"))

    assert exc_info.value.status_code == 404
    receipt_repository.commit.assert_not_awaited()
