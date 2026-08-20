import pytest

from app.application.commands.email_templates.create_email_template import CreateEmailTemplateCommand
from app.domain.email_templates.email_schemas import CreateEmailTemplateSchema
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def command(email_template_repository):
    return CreateEmailTemplateCommand(email_template_repository=email_template_repository)


async def test_create_email_template_success(command, email_template_repository):
    data = CreateEmailTemplateSchema(
        email_type="WELCOME", subject="Hi", text_content="text", html_content="<p>html</p>", is_active=True
    )

    email_template = await command(email_template_data=data)

    assert email_template.subject == "Hi"
    email_template_repository.add.assert_called_once_with(email_template)
    email_template_repository.commit.assert_awaited_once()
