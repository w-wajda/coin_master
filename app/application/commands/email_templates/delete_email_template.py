from uuid import UUID

from starlette import status

from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.domain.exceptions import HTTPException


class DeleteEmailTemplateCommand:
    def __init__(self, email_template_repository: IEmailTemplateRepository):
        self.email_template_repository = email_template_repository

    async def __call__(self, uuid: UUID) -> None:
        async with self.email_template_repository.start_session():
            if email_template := await self.email_template_repository.get_by(uuid=uuid):
                await self.email_template_repository.delete(email_template)
                await self.email_template_repository.commit()
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")
