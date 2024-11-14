from abc import ABC

from app.domain.common.repository import IBaseRepository
from app.domain.email_templates.email import EmailTemplate


class IEmailTemplateRepository(IBaseRepository[EmailTemplate], ABC):
    pass
