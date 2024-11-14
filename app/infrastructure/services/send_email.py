from fastapi_mail import (
    FastMail as BaseFastMail,
    MessageSchema,
)
from fastapi_mail.connection import Connection
from fastapi_mail.errors import PydanticClassRequired
from fastapi_mail.fastmail import email_dispatched
from jinja2 import Environment

from app.domain.email_templates.email import EmailTemplate


class FastMail(BaseFastMail):
    async def send_mail(self, message: MessageSchema, email_template: EmailTemplate) -> None:
        if not isinstance(email_template, EmailTemplate):
            raise ValueError("Template should be provided from EmailTemplate class")

        if not isinstance(message, MessageSchema):
            raise PydanticClassRequired("Message schema should be provided from MessageSchema class")

        template = Environment().from_string(email_template.html_content)
        msg = await self.__prepare_message(message, template)

        async with Connection(self.config) as session:
            if not self.config.SUPPRESS_SEND:
                await session.session.send_message(msg)

            email_dispatched.send(msg)
