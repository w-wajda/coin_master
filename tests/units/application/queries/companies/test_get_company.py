import uuid
from unittest.mock import MagicMock

import pytest

from app.application.queries.companies.get_company import GetCompanyQuery
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
    return GetCompanyQuery(user_repository=user_repository, company_repository=company_repository)


async def test_get_company_success(query, user_repository, company_repository):
    user_repository.get.return_value = object()
    company = MagicMock()
    company_repository.get_by.return_value = company

    result = await query(user_id=1, uuid=uuid.uuid4())

    assert result is company


async def test_get_company_user_not_found(query, user_repository, company_repository):
    user_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    company_repository.get_by.assert_not_awaited()


async def test_get_company_not_found(query, user_repository, company_repository):
    user_repository.get.return_value = object()
    company_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(user_id=1, uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
