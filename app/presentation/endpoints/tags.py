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
from starlette.requests import Request

from app.application.commands.tags.create_tag import CreateTagCommand
from app.application.commands.tags.delete_tag import DeleteTagCommand
from app.application.commands.tags.update_tag import UpdateTagCommand
from app.application.queries.tags.get_tag import GetTagQuery
from app.application.queries.tags.get_tag_list import GetTagListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.tags.tag_schemas import (
    CreateTagSchema,
    TagSchema,
)
from app.infrastructure.decorators import requires_auth
from app.infrastructure.di import AppContainer


routes = APIRouter()


@routes.get("/{uuid}/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_tag(
    request: Request,
    uuid: UUID,
    get_tag_query: GetTagQuery = Depends(Provide[AppContainer.queries.get_tag]),
) -> TagSchema:
    tag = await get_tag_query(user_id=request.user.id, uuid=uuid)
    return TagSchema.model_validate(tag)


@routes.get("/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_tag_list(
    request: Request,
    get_tag_list_query: GetTagListQuery = Depends(Provide[AppContainer.queries.get_tag_list]),
    pagination: PaginationService = Depends(),
) -> PaginatedSchema[TagSchema]:
    tags = await get_tag_list_query(user_id=request.user.id, limit=pagination.limit, offset=pagination.offset)
    return pagination.get_items(tags)


@routes.post("/", tags=["Authenticated"], status_code=status.HTTP_201_CREATED)
@requires_auth()
@inject
async def create_tag(
    request: Request,
    tag_data: CreateTagSchema,
    create_tag_command: CreateTagCommand = Depends(Provide[AppContainer.commands.create_tag]),
) -> TagSchema:
    tag = await create_tag_command(user_id=request.user.id, tag_data=tag_data)
    return TagSchema.model_validate(tag)


@routes.patch("/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_200_OK)
@requires_auth()
@inject
async def update_tag(
    request: Request,
    uuid: UUID,
    tag_data: CreateTagSchema,
    update_tag_command: UpdateTagCommand = Depends(Provide[AppContainer.commands.update_tag]),
) -> TagSchema:
    tag = await update_tag_command(user_id=request.user.id, uuid=uuid, tag_data=tag_data)
    return TagSchema.model_validate(tag)


@routes.delete("/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_204_NO_CONTENT)
@requires_auth()
@inject
async def delete_tag(
    request: Request,
    uuid: UUID,
    delete_tag_command: DeleteTagCommand = Depends(Provide[AppContainer.commands.delete_tag]),
) -> None:
    await delete_tag_command(user_id=request.user.id, uuid=uuid)
