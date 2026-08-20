import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.email_templates.delete_email_template import DeleteEmailTemplateCommand
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def command(email_template_repository):
    return DeleteEmailTemplateCommand(email_template_repository=email_template_repository)


async def test_delete_email_template_success(command, email_template_repository):
    email_template = MagicMock()
    email_template_repository.get_by.return_value = email_template

    result = await command(uuid=uuid.uuid4())

    assert result is None
    email_template_repository.delete.assert_awaited_once_with(email_template)
    email_template_repository.commit.assert_awaited_once()


async def test_delete_email_template_not_found(command, email_template_repository):
    email_template_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(uuid=uuid.uuid4())

    assert exc_info.value.status_code == 404
    email_template_repository.delete.assert_not_awaited()
    email_template_repository.commit.assert_not_awaited()
