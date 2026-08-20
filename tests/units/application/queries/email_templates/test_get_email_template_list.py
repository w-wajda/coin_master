from unittest.mock import MagicMock

import pytest

from app.application.queries.email_templates.get_email_template_list import GetEmailTemplateListQuery
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def query(email_template_repository):
    return GetEmailTemplateListQuery(email_template_repository=email_template_repository)


async def test_get_email_template_list_success(query, email_template_repository):
    templates = [MagicMock(), MagicMock()]
    email_template_repository.get_list.return_value = templates
    email_template_repository.count.return_value = 2

    result = await query(limit=10, offset=0)

    assert result == (templates, 2)
    email_template_repository.get_list.assert_awaited_once_with(limit=10, offset=0)
    email_template_repository.count.assert_awaited_once_with()
