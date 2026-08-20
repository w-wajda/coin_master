import pytest

from app.application.commands.companies.create_company import CreateCompanyCommand
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
    return CreateCompanyCommand(user_repository=user_repository, company_repository=company_repository)


async def test_create_company_success(command, user_repository, company_repository):
    user_repository.get.return_value = object()

    company = await command(user_id=1, company_data=CreateCompanySchema(name="Biedronka", address="Main St 1"))

    assert company.user_id == 1
    company_repository.add.assert_called_once_with(company)
    company_repository.commit.assert_awaited_once()


async def test_create_company_user_not_found(command, user_repository, company_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(user_id=1, company_data=CreateCompanySchema(name="Biedronka", address="Main St 1"))

    assert exc_info.value.status_code == 404
    company_repository.add.assert_not_called()
