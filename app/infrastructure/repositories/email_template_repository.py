from app.domain.email_templates.email import EmailTemplate
from app.domain.email_templates.email_repository import IEmailTemplateRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyEmailTemplateRepository(IEmailTemplateRepository, GenericSQLAlchemyRepository[EmailTemplate]):
    model = EmailTemplate
