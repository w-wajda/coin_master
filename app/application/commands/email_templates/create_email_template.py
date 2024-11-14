from app.domain.email_templates.email import EmailTemplate
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.domain.email_templates.email_schemas import CreateEmailTemplateSchema


class CreateEmailTemplateCommand:
    def __init__(self, email_template_repository: IEmailTemplateRepository):
        self.email_template_repository = email_template_repository

    async def __call__(self, email_template_data: CreateEmailTemplateSchema) -> EmailTemplate:
        async with self.email_template_repository.start_session():
            email_template = EmailTemplate(**email_template_data.model_dump())

            self.email_template_repository.add(email_template)
            await self.email_template_repository.commit()
            return email_template
