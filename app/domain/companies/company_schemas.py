from uuid import UUID

from pydantic import ConfigDict, BaseModel


class CompanySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    address: str


class CreateCompanySchema(BaseModel):
    name: str
    address: str


class UpdateCompanySchema(CreateCompanySchema):
    uuid: UUID