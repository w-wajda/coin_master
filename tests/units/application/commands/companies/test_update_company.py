import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.companies.update_company import UpdateCompanyCommand
from app.domain.companies.company_schemas import CreateCompanySchema
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
    return UpdateCompanyCommand(user_repository=user_repository, company_repository=company_repository)


async def test_update_company_success(command, user_repository, company_repository):
    user_repository.get.return_value = object()
    company = MagicMock()
    company_repository.get_by.return_value = company

    company_data = CreateCompanySchema(name="Lidl", address="Other St 2")
    result = await command(user_id=1, uuid=uuid.uuid4(), company_data=company_data)

    assert result is company
    company.update.assert_called_once_with(**company_data.model_dump(exclude_unset=True))
    company_repository.commit.assert_awaited_once()


async def test_update_company_user_not_found(command, user_repository, company_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), company_data=CreateCompanySchema(name="Lidl", address="x"))

    assert exc_info.value.status_code == 404
    company_repository.get_by.assert_not_awaited()


async def test_update_company_not_found(command, user_repository, company_repository):
    user_repository.get.return_value = object()
    company_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, uuid=uuid.uuid4(), company_data=CreateCompanySchema(name="Lidl", address="x"))

    assert exc_info.value.status_code == 404
    company_repository.commit.assert_not_awaited()
