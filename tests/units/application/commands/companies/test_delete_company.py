import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.companies.delete_company import DeleteCompanyCommand
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def company_repository():
    return make_repository()


@pytest.fixture
def command(user_repository, company_repository):
    return DeleteCompanyCommand(user_repository=user_repository, company_repository=company_repository)


async def test_delete_company_success(command, user_repository, company_repository):
    user_repository.get.return_value = object()
    company = MagicMock()
    company_repository.get_by.return_value = company

    result = await command(user_id=1, uuid=uuid.uuid4())

    assert result is None
    company_repository.delete.assert_awaited_once_with(company)
    company_repository.commit.assert_awaited_once()


async def test_delete_company_user_not_found(command, user_repository, company_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    company_repository.delete.assert_not_awaited()


async def test_delete_company_not_found(command, user_repository, company_repository):
    user_repository.get.return_value = object()
    company_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    company_repository.delete.assert_not_awaited()
    company_repository.commit.assert_not_awaited()
