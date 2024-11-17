from uuid import UUID

from starlette import status

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.exceptions import HTTPException


class GetCompanyQuery:
    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository

    async def __call__(self, uuid: UUID) -> Company:
        async with self.company_repository.start_session():
            pass

        if company := await self.company_repository.get_by(uuid=uuid):
            return company
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUNDT, detail="Company not found")
