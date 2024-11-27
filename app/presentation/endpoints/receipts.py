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

from app.application.commands.items.create_item import CreateItemCommand
from app.application.commands.items.delete_item import DeleteItemCommand
from app.application.commands.items.update_item import UpdateItemCommand
from app.application.queries.items.get_item_list import GetItemListQuery
from app.application.services.pagination import (
    PaginatedSchema,
    PaginationService,
)
from app.domain.items.item_schemas import (
    CreateItemSchema,
    ItemSchema,
)
from app.infrastructure.decorators import requires_auth
from app.infrastructure.di import AppContainer


routes = APIRouter()


@routes.get("/{receipt_uuid}/items/", tags=["Authenticated"])
@requires_auth()
@inject
async def get_item_list(
    request: Request,
    receipt_uuid: UUID,
    get_item_list_query: GetItemListQuery = Depends(Provide[AppContainer.queries.get_item_list]),
    pagination: PaginationService = Depends(),
) -> PaginatedSchema[ItemSchema]:
    items = await get_item_list_query(
        user_id=request.user.id, receipt_uuid=receipt_uuid, limit=pagination.limit, offset=pagination.offset
    )
    return pagination.get_items(items)


@routes.post("/{receipt_uuid}/items/", tags=["Authenticated"], status_code=status.HTTP_201_CREATED)
@requires_auth()
@inject
async def create_item(
    request: Request,
    receipt_uuid: UUID,
    item_data: CreateItemSchema,
    create_item_command: CreateItemCommand = Depends(Provide[AppContainer.commands.create_item]),
) -> ItemSchema:
    item = await create_item_command(user_id=request.user.id, receipt_uuid=receipt_uuid, item_data=item_data)
    return ItemSchema.model_validate(item)


@routes.patch("/{receipt_uuid}/items/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_200_OK)
@requires_auth()
@inject
async def update_item(
    request: Request,
    receipt_uuid: UUID,
    uuid: UUID,
    item_data: CreateItemSchema,
    update_item_command: UpdateItemCommand = Depends(Provide[AppContainer.commands.update_item]),
) -> ItemSchema:
    item = await update_item_command(user_id=request.user.id, receipt_uuid=receipt_uuid, uuid=uuid, item_data=item_data)
    return ItemSchema.model_validate(item)


@routes.delete("/{receipt_uuid}/items/{uuid}/", tags=["Authenticated"], status_code=status.HTTP_204_NO_CONTENT)
@requires_auth()
@inject
async def delete_item(
    request: Request,
    receipt_uuid: UUID,
    uuid: UUID,
    delete_item_command: DeleteItemCommand = Depends(Provide[AppContainer.commands.delete_item]),
) -> None:
    await delete_item_command(user_id=request.user.id, receipt_uuid=receipt_uuid, uuid=uuid)
