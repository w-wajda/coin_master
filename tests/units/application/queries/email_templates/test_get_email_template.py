import uuid
from unittest.mock import MagicMock

import pytest

from app.application.queries.email_templates.get_email_template import GetEmailTemplateQuery
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def query(email_template_repository):
    return GetEmailTemplateQuery(email_template_repository=email_template_repository)


async def test_get_email_template_success(query, email_template_repository):
    email_template = MagicMock()
    email_template_repository.get_by.return_value = email_template

    result = await query(uuid=uuid.uuid4())

    assert result is email_template


async def test_get_email_template_not_found(query, email_template_repository):
    email_template_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await query(uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
