from uuid import UUID

from starlette import status

from app.domain.exceptions import HTTPException
from app.domain.tags.tag import Tag
from app.domain.tags.tag_repository import ITagRepository
from app.domain.tags.tag_schemas import CreateTagSchema
from app.domain.users.user_repository import IUserRepository


class UpdateTagCommand:
    def __init__(self, user_repository: IUserRepository, tag_repository: ITagRepository):
        self.user_repository = user_repository
        self.tag_repository = tag_repository

    async def __call__(self, user_id: int, uuid: UUID, tag_data: CreateTagSchema) -> Tag:
        async with self.user_repository.start_session() as session:
            self.tag_repository.use_session(session)

            user = await self.user_repository.get(user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            if tag := await self.tag_repository.get_by(user=user, uuid=uuid):
                tag.update(**tag_data.model_dump(exclude_unset=True))
                await self.tag_repository.commit()
                return tag

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
