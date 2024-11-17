from uuid import UUID

from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
)

from app.application.queries.companies.get_company import GetCompanyQuery
from app.application.queries.companies.get_company_list import GetCompanyListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.companies.company_schemas import CompanySchema
from app.infrastructure.decorators import requires_auth
from app.infrastructure.di import AppContainer


routes = APIRouter()


@routes.get("/get/{uuid}/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_company(
    uuid: UUID,
    get_company_query: GetCompanyQuery = Depends(Provide[AppContainer.queries.get_company]),
) -> CompanySchema:
    company = await get_company_query(uuid)
    return CompanySchema.model_validate(company)


@routes.get("/get_list/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_company_list(
    get_company_list_query: GetCompanyListQuery = Depends(Provide[AppContainer.queries.get_company_list]),
    pagination: PaginationService = Depends(),
) -> PaginatedSchema[CompanySchema]:
    companies = await get_company_list_query(limit=pagination.limit, offset=pagination.offset)
    return pagination.get_items(companies)
