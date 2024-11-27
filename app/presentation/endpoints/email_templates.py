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

from app.application.commands.email_templates.create_email_template import CreateEmailTemplateCommand
from app.application.commands.email_templates.delete_email_template import DeleteEmailTemplateCommand
from app.application.commands.email_templates.update_email_template import UpdateEmailTemplateCommand
from app.application.queries.email_templates.get_email_template import GetEmailTemplateQuery
from app.application.queries.email_templates.get_email_template_list import GetEmailTemplateListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.email_templates.email_schemas import (
    CreateEmailTemplateSchema,
    EmailTemplateSchema,
)
from app.infrastructure.decorators import requires_auth
from app.infrastructure.di import AppContainer


routes = APIRouter()


@routes.get("/{uuid}/", tags=["Authenticated"])
@requires_auth("is_staff")
@inject
async def get_email_template(
    uuid: UUID,
    get_email_template_query: GetEmailTemplateQuery = Depends(Provide[AppContainer.queries.get_email_template]),
) -> EmailTemplateSchema:
    email_template = await get_email_template_query(uuid=uuid)
    return EmailTemplateSchema.model_validate(email_template)


@routes.get("/", tags=["Authenticated"])
@requires_auth("is_staff")
@inject
async def get_email_template_list(
    get_email_template_list_query: GetEmailTemplateListQuery = Depends(
        Provide[AppContainer.queries.get_email_template_list]
    ),
    pagination: PaginationService = Depends(),
) -> PaginatedSchema[EmailTemplateSchema]:
    email_templates = await get_email_template_list_query(limit=pagination.limit, offset=pagination.offset)
    return pagination.get_items(email_templates)


@routes.post("/", tags=["Authenticated"], status_code=status.HTTP_201_CREATED)
@requires_auth("is_staff")
@inject
async def create_email_template(
    email_template_data: CreateEmailTemplateSchema,
    create_email_template_command: CreateEmailTemplateCommand = Depends(
        Provide[AppContainer.commands.create_email_template]
    ),
) -> EmailTemplateSchema:
    email_template = await create_email_template_command(email_template_data=email_template_data)
    return EmailTemplateSchema.model_validate(email_template)


@routes.patch("/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_200_OK)
@requires_auth("is_staff")
@inject
async def update_email_template(
    uuid: UUID,
    email_template_data: CreateEmailTemplateSchema,
    update_email_template_command: UpdateEmailTemplateCommand = Depends(
        Provide[AppContainer.commands.update_email_template]
    ),
) -> EmailTemplateSchema:
    email_template = await update_email_template_command(uuid=uuid, email_template_data=email_template_data)
    return EmailTemplateSchema.model_validate(email_template)


@routes.delete("/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_204_NO_CONTENT)
@requires_auth("is_staff")
@inject
async def delete_email_template(
    uuid: UUID,
    delete_email_template_command: DeleteEmailTemplateCommand = Depends(
        Provide[AppContainer.commands.delete_email_template]
    ),
) -> None:
    await delete_email_template_command(uuid=uuid)
