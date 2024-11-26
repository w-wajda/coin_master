from starlette import status

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.companies.company_schemas import CreateCompanySchema
from app.domain.exceptions import HTTPException
from app.domain.users.user_repository import IUserRepository


class CreateCompanyCommand:
    def __init__(self, user_repository: IUserRepository, company_repository: ICompanyRepository):
        self.user_repository = user_repository
        self.company_repository = company_repository

    async def __call__(self, user_id: int, company_data: CreateCompanySchema) -> Company:
        async with self.user_repository.start_session() as session:
            self.company_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            company = Company(**company_data.model_dump())
            company.user_id = user_id

            self.company_repository.add(company)
            await self.company_repository.commit()
            return company
