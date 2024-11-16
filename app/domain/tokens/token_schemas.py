from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    token: str = Field(...)
    is_active: bool


class TokenCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token: str = Field(...)


