from uuid import UUID

from starlette import status

from app.domain.companies.company_repository import ICompanyRepository
from app.domain.exceptions import HTTPException


class DeleteCompanyCommand:
    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository

    async def __call__(self, uuid: UUID) -> None:
        async with self.company_repository.start_session():

            if company := await self.company_repository.get_by(uuid=uuid):
                await self.company_repository.delete(company)
                await self.company_repository.commit()

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
