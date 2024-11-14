import logging
from typing import Optional

from fastapi_mail import (
    ConnectionConfig,
    MessageSchema,
    MessageType,
)

from app.domain.email_templates.email import EmailTypeEnum
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.infrastructure.conf import Settings
from app.infrastructure.services.send_email import FastMail


logger = logging.getLogger(__name__)


class SendEmailService:
    def __init__(self, email_template_repository: IEmailTemplateRepository, config: Settings):
        self.fast_mail = FastMail(
            config=ConnectionConfig(
                MAIL_USERNAME=config.EMAIL_URL.username or "",
                MAIL_PASSWORD=config.EMAIL_URL.password or "",
                MAIL_FROM=config.EMAIL_FROM,
                MAIL_FROM_NAME=config.EMAIL_FROM_NAME,
                MAIL_PORT=config.EMAIL_URL.port or 25,
                MAIL_SERVER=config.EMAIL_URL.host or "localhost",
                MAIL_STARTTLS=config.EMAIL_URL.scheme == "smtp+tls",
                MAIL_SSL_TLS=config.EMAIL_URL.scheme == "smtp+ssl",
                USE_CREDENTIALS=bool(config.EMAIL_URL.username and config.EMAIL_URL.password),
                SUPPRESS_SEND=config.EMAIL_URL.scheme == "test",
            )
        )
        self.email_template_repository = email_template_repository

    async def send(
        self, email_type: EmailTypeEnum, email: str, context: Optional[dict] = None, language: Optional[str] = None
    ):
        async with self.email_template_repository.start_session():
            email_template = await self.email_template_repository.get_by(
                email_type=email_type, language=language, is_active=True
            )

            if not email_template:
                logger.error(f"Email template not found for {email_type=}, {language=}")
                return

            message = MessageSchema(
                subject=email_template.subject,
                recipients=[email],
                template_body=context,
                subtype=MessageType.html,
            )

            await self.fast_mail.send_mail(message, email_template=email_template)
