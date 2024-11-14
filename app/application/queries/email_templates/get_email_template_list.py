from typing import Iterable

from app.domain.email_templates.email import EmailTemplate
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.infrastructure.conf import settings


class GetEmailTemplateListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, email_template_repository: IEmailTemplateRepository):
        self.email_template_repository = email_template_repository

    async def __call__(self, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[EmailTemplate]:
        async with self.email_template_repository.start_session():
            pass

        return await self.email_template_repository.get_list(limit=limit, offset=offset)
