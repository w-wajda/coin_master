from typing import Iterable

from app.domain.companies.company import Company
from app.domain.companies.company_repository import ICompanyRepository
from app.infrastructure.conf import settings


class GetCompanyListQuery:
    DEFAULT_LIMIT = settings.PAGINATION_DEFAULT_LIMIT

    def __init__(self, company_repository: ICompanyRepository):
        self.company_repository = company_repository

    async def __call__(self, limit: int = DEFAULT_LIMIT, offset: int = 0) -> Iterable[Company]:
        async with self.company_repository.start_session():
            pass

        return await self.company_repository.get_list(limit=limit, offset=offset)
