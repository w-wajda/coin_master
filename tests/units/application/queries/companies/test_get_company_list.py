from unittest.mock import MagicMock

import pytest

from app.application.queries.companies.get_company_list import GetCompanyListQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def user_repository():
    return make_repository()


@pytest.fixture
def company_repository():
    return make_repository()


@pytest.fixture
def query(user_repository, company_repository):
    return GetCompanyListQuery(user_repository=user_repository, company_repository=company_repository)


async def test_get_company_list_success(query, user_repository, company_repository):
    user_repository.get.return_value = object()
    companies = [MagicMock(), MagicMock()]
    company_repository.get_list.return_value = companies

    result = await query(user_id=1, limit=10, offset=0)

    assert result is companies
    company_repository.get_list.assert_awaited_once_with(user_id=1, limit=10, offset=0)


async def test_get_company_list_user_not_found(query, user_repository, company_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1)

    assert exc_info.value.status_code == 404
    company_repository.get_list.assert_not_awaited()
