import uuid
from unittest.mock import MagicMock

import pytest

from app.application.commands.email_templates.update_email_template import UpdateEmailTemplateCommand
from app.domain.email_templates.email_schemas import CreateEmailTemplateSchema
from app.domain.exceptions import HTTPException
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def command(email_template_repository):
    return UpdateEmailTemplateCommand(email_template_repository=email_template_repository)


def _data():
    return CreateEmailTemplateSchema(
        email_type="WELCOME", subject="Hi", text_content="text", html_content="<p>html</p>", is_active=True
    )


async def test_update_email_template_success(command, email_template_repository):
    email_template = MagicMock()
    email_template_repository.get_by.return_value = email_template

    data = _data()
    result = await command(uuid=uuid.uuid4(), email_template_data=data)

    assert result is email_template
    email_template.update.assert_called_once_with(**data.model_dump(exclude_unset=True))
    email_template_repository.commit.assert_awaited_once()


async def test_update_email_template_not_found(command, email_template_repository):
    email_template_repository.get_by.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await command(uuid=uuid.uuid4(), email_template_data=_data())

    assert exc_info.value.status_code == 404
    email_template_repository.commit.assert_not_awaited()
