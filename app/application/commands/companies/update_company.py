from uuid import UUID

from starlette import status

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.companies.company_schemas import UpdateCompanySchema
from app.domain.exceptions import HTTPException


class UpdateCompanyCommand:
    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository

    async def __call__(self, uuid: UUID, company_data: UpdateCompanySchema) -> Company:
        async with self.company_repository.start_session():
            if company := await self.company_repository.get_by(uuid=uuid):
                company.update(**company_data.model_dump(exclude_unset=True))
                await self.company_repository.commit()
                return company

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
