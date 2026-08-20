import pytest

from app.application.commands.receipts.create_receipt import CreateReceiptCommand
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
    return CreateReceiptCommand(user_repository=user_repository, receipt_repository=receipt_repository)


async def test_create_receipt_success(command, user_repository, receipt_repository):
    user_repository.get.return_value = object()

    receipt = await command(user_id=1, receipt_data=CreateReceiptSchema(amount="10.50", scan_file="receipt.jpg"))

    assert receipt.user_id == 1
    assert receipt.amount == pytest.approx(10.50)
    receipt_repository.add.assert_called_once_with(receipt)
    receipt_repository.commit.assert_awaited_once()


async def test_create_receipt_user_not_found(command, user_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, receipt_data=CreateReceiptSchema(amount="10.50", scan_file="receipt.jpg"))

    assert exc_info.value.status_code == 404
    receipt_repository.add.assert_not_called()
    receipt_repository.commit.assert_not_awaited()
