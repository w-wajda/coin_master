from uuid import UUID

from starlette import status

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.exceptions import HTTPException
from app.domain.users.user_repository import IUserRepository


class GetCompanyQuery:
    def __init__(
        self,
        user_repository: IUserRepository,
        company_repository: ICompanyRepository,
    ):
        self.user_repository = user_repository
        self.company_repository = company_repository

    async def __call__(self, user_id: int, uuid: UUID) -> Company:
        async with self.user_repository.start_session() as session:
            self.company_repository.use_session(session)

        user = await self.user_repository.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if company := await self.company_repository.get_by(user=user, uuid=uuid):
            return company

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUNDT, detail="Company not found")
