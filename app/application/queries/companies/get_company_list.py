from typing import Iterable

from starlette import status

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.domain.exceptions import HTTPException
from app.domain.users.user_repository import IUserRepository
from app.infrastructure.conf import settings


class GetCompanyListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, user_repository: IUserRepository, company_repository: ICompanyRepository):
        self.user_repository = user_repository
        self.company_repository = company_repository

    async def __call__(self, user_id: int, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Company]:
        async with self.user_repository.start_session() as session:
            self.company_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            return await self.company_repository.get_list(user=user, limit=limit, offset=offset)
