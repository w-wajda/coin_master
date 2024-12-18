from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class TagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str


class CreateTagSchema(BaseModel):
    name: str
    address: str
