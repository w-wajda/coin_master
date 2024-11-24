from uuid import UUID

from starlette import status

from app.domain.email_templates.email import EmailTemplate
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.domain.email_templates.email_schemas import CreateEmailTemplateSchema
from app.domain.exceptions import HTTPException


class UpdateEmailTemplateCommand:
    def __init__(self, email_template_repository: IEmailTemplateRepository):
        self.email_template_repository = email_template_repository

    async def __call__(self, uuid: UUID, email_template_data: CreateEmailTemplateSchema) -> EmailTemplate:
        async with self.email_template_repository.start_session():
            if email_template := await self.email_template_repository.get_by(uuid=uuid):
                email_template.update(**email_template_data.model_dump(exclude_unset=True))
                await self.email_template_repository.commit()
                return email_template

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")
