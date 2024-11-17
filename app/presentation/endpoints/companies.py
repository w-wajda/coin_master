from uuid import UUID

from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from app.application.commands.companies.create_company import CreateCompanyCommand
from app.application.commands.companies.delete_company import DeleteCompanyCommand
from app.application.commands.companies.update_company import UpdateCompanyCommand
from app.application.queries.companies.get_company import GetCompanyQuery
from app.application.queries.companies.get_company_list import GetCompanyListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.companies.company_schemas import (
    CompanySchema,
    CreateCompanySchema,
    UpdateCompanySchema,
)
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


@routes.post("/create/", tags=["Authenticated"], status_code=status.HTTP_201_CREATED)
@requires_auth()
@inject
async def create_company(
    company_data: CreateCompanySchema,
    create_company_command: CreateCompanyCommand = Depends(Provide[AppContainer.commands.create_company]),
) -> CompanySchema:
    company = await create_company_command(company_data)
    return CompanySchema.model_validate(company)


@routes.patch("/update/{uuid}", tags=["Authenticated"], status_code=status.HTTP_200_OK)
@requires_auth()
@inject
async def update_company(
    uuid: UUID,
    company_data: UpdateCompanySchema,
    update_company_command: UpdateCompanyCommand = Depends(Provide[AppContainer.commands.update_company]),
) -> CompanySchema:
    company = await update_company_command(uuid, company_data)
    return CompanySchema.model_validate(company)


@routes.delete("/delete/{uuid}", tags=["Authenticated"], status_code=status.HTTP_204_NO_CONTENT)
@requires_auth()
@inject
async def delete_company(
    uuid: UUID,
    delete_company_command: DeleteCompanyCommand = Depends(Provide[AppContainer.commands.delete_company]),
) -> None:
    await delete_company_command(uuid)
