from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class EmailTemplateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    email_type: str
    subject: str
    text_content: str
    html_content: str
    is_active: bool


class CreateEmailTemplateSchema(BaseModel):
    email_type: str
    subject: str
    text_content: str
    html_content: str
    is_active: bool
