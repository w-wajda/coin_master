from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TokenCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str = Field(...)


class TokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: UUID

    token: str = Field(...)
    created: datetime

    client: Optional[str] = None
    device_type: Optional[str] = None

