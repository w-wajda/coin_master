from uuid import UUID

from starlette import status

from app.domain.email_templates.email import EmailTemplate
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.domain.exceptions import HTTPException


class GetEmailTemplateQuery:
    def __init__(self, email_template_repository: IEmailTemplateRepository):
        self.email_template_repository = email_template_repository

    async def __call__(self, uuid: UUID) -> EmailTemplate:
        async with self.email_template_repository.start_session():
            pass

        if email_template := await self.email_template_repository.get_by(uuid=uuid):
            return email_template
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")
