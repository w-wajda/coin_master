from starlette import status

from app.domain.exceptions import HTTPException


class UserDoesNotExist(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found."

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class EmailAlreadyRegistered(HTTPException):
    def __init__(self, email: str):
        self.email = email
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "One or more validation errors occurred."
        self.errors = {
            "email": ["Email is already registered"],
        }

    def __str__(self):
        return f"Email '{self.email}' is already registered."


class InvalidUserCredentials(HTTPException):
    def __init__(self, email: str):
        self.email = email
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "One or more validation errors occurred."
        self.errors = {
            "": ["Invalid email or password"],
        }

    def __str__(self):
        return "Invalid email or password."


class InvalidOldPassword(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.errors = {
            "old_password": ["Invalid old password"],
        }
        self.detail = "One or more validation errors occurred."

    def __str__(self):
        return "Invalid old password."
