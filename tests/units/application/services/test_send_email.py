from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from app.application.services.send_email import SendEmailService
from app.domain.email_templates.email import EmailTypeEnum
from app.infrastructure.conf import settings
from tests.units.application._helpers import make_repository


@pytest.fixture
def email_template_repository():
    return make_repository()


@pytest.fixture
def service(email_template_repository):
    service = SendEmailService(email_template_repository=email_template_repository, config=settings)
    service.fast_mail.send_mail = AsyncMock()
    return service


async def test_send_dispatches_mail_when_template_found(service, email_template_repository):
    email_template = MagicMock(subject="Welcome", html_content="<p>Hi</p>")
    email_template_repository.get_by.return_value = email_template

    await service.send(email_type=EmailTypeEnum.WELCOME, email="user@example.com", context={"name": "A"})

    email_template_repository.get_by.assert_awaited_once_with(
        email_type=EmailTypeEnum.WELCOME, language=None, is_active=True
    )
    service.fast_mail.send_mail.assert_awaited_once()
    message = service.fast_mail.send_mail.call_args.args[0]
    assert [recipient.email for recipient in message.recipients] == ["user@example.com"]


async def test_send_skips_when_template_missing(service, email_template_repository):
    email_template_repository.get_by.return_value = None

    await service.send(email_type=EmailTypeEnum.WELCOME, email="user@example.com")

    service.fast_mail.send_mail.assert_not_awaited()
