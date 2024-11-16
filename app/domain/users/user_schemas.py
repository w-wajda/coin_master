from typing import (
    Annotated,
    Optional,
)
from uuid import UUID

import annotated_types as at
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    email: Optional[EmailStr]


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(..., examples=["user@test.pl"])
    password: Annotated[str, at.MinLen(8)] = Field(exclude=True, examples=["password123"])


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., examples=["user@test.pl"])
    password: str = Field(..., examples=["password123"])


class ChangePasswordSchema(BaseModel):
    old_password: str

    password1: Annotated[str, at.MinLen(8)] = Field(exclude=True, examples=["password123"])
    password2: str = Field(exclude=True, examples=["password123"])

    @field_validator("password2")
    @classmethod
    def check_passwords_match(cls, password2, info: ValidationInfo) -> str:
        if "password1" in info.data and password2 != info.data.get("password1", ""):
            raise ValueError("passwords must match")
        return password2


class ResetPasswordSchema(BaseModel):
    email: EmailStr = Field(..., examples=["user@test.com"])


class ChangePasswordWithTokenSchema(BaseModel):
    token: str = Field(..., examples=["token123"])

    password1: Annotated[str, at.MinLen(8)] = Field(exclude=True, examples=["password123"])
    password2: str = Field(exclude=True, examples=["password123"])

    @field_validator("password2")
    @classmethod
    def check_passwords_match(cls, password2, info: ValidationInfo) -> str:
        if "password1" in info.data and password2 != info.data.get("password1", ""):
            raise ValueError("passwords must match")
        return password2
