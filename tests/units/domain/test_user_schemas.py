import pytest
from pydantic import ValidationError

from app.domain.users.user_schemas import (
    ChangePasswordSchema,
    ChangePasswordWithTokenSchema,
)


def test_change_password_schema_rejects_mismatched_passwords():
    with pytest.raises(ValidationError):
        ChangePasswordSchema(old_password="old12345", password1="new123456", password2="different1")


def test_change_password_with_token_schema_rejects_mismatched_passwords():
    with pytest.raises(ValidationError):
        ChangePasswordWithTokenSchema(token="abc", password1="new123456", password2="different1")
