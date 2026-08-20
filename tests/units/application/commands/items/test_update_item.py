import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.items.update_item import UpdateItemCommand
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
    return UpdateItemCommand(
        user_repository=user_repository, item_repository=item_repository, receipt_repository=receipt_repository
    )


async def test_update_item_success(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = MagicMock(id=42)
    item = MagicMock()
    item_repository.get_by.return_value = item

    item_data = CreateItemSchema(name="Chleb", price="5.49")
    result = await command(user_id=1, receipt_uuid=uuid.uuid4(), uuid=uuid.uuid4(), item_data=item_data)

    assert result is item
    item.update.assert_called_once_with(**item_data.model_dump(exclude_unset=True))
    item_repository.commit.assert_awaited_once()


async def test_update_item_user_not_found(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(
            user_id=1, receipt_uuid=uuid.uuid4(), uuid=uuid.uuid4(), item_data=CreateItemSchema(name="x", price="1")
        )

    assert exc_info.value.status_code == 404
    receipt_repository.get_by.assert_not_awaited()


async def test_update_item_receipt_not_found(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(
            user_id=1, receipt_uuid=uuid.uuid4(), uuid=uuid.uuid4(), item_data=CreateItemSchema(name="x", price="1")
        )

    assert exc_info.value.status_code == 404
    item_repository.get_by.assert_not_awaited()


async def test_update_item_not_found(command, user_repository, item_repository, receipt_repository):
    user_repository.get.return_value = object()
    receipt_repository.get_by.return_value = MagicMock(id=42)
    item_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(
            user_id=1, receipt_uuid=uuid.uuid4(), uuid=uuid.uuid4(), item_data=CreateItemSchema(name="x", price="1")
        )

    assert exc_info.value.status_code == 404
    item_repository.commit.assert_not_awaited()
