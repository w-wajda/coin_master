import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.items.create_item import CreateItemCommand
from app.domain.exceptions import HTTPException
from app.domain.items.item_schemas import CreateItemSchema
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
def command(user_repository, item_repository, receipt_repository):
    return CreateItemCommand(
        user_repository=user_repository, item_repository=item_repository, receipt_repository=receipt_repository
    )


async def test_create_item_success(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt = MagicMock(id=42)
    receipt_repository.get_by.return_value = receipt

    item = await command(
        user_id=1, receipt_uuid=uuid.uuid4(), item_data=CreateItemSchema(name="Mleko", price="4.99")
    )

    assert item.receipt_id == 42
    item_repository.add.assert_called_once_with(item)
    item_repository.commit.assert_awaited_once()


async def test_create_item_user_not_found(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, receipt_uuid=uuid.uuid4(), item_data=CreateItemSchema(name="Mleko", price="4.99"))

    assert exc_info.value.status_code == 404
    receipt_repository.get_by.assert_not_awaited()
    item_repository.add.assert_not_called()


async def test_create_item_receipt_not_found(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, receipt_uuid=uuid.uuid4(), item_data=CreateItemSchema(name="Mleko", price="4.99"))

    assert exc_info.value.status_code == 404
    item_repository.add.assert_not_called()
