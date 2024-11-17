from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.companies.company_schemas import CreateCompanySchema


class CreateCompanyCommand:
    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository

    async def __call__(self, company_data: CreateCompanySchema) -> Company:
        async with self.company_repository.start_session():
            company = Company(**company_data.model_dump())

        self.company_repository.add(company)
        await self.company_repository.commit()
        return company
