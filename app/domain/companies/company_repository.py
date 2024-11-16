from abc import ABC

from app.domain.common.repository import IBaseRepository
from app.domain.companies.company import Company


class ICompanyRepository(IBaseRepository[Company], ABC):
    pass
