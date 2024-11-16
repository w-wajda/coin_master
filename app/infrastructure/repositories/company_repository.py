from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.infrastructure.repositories.base_sqlalchemy_repository import GenericSQLAlchemyRepository


class SQLAlchemyCompanyRepository(ICompanyRepository, GenericSQLAlchemyRepository[Company]):
    model = Company
