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
