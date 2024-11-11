from typing import (
    Dict,
    List,
    Optional,
)

from fastapi import HTTPException as BaseHTTPException


class ObjectDoesNotExist(Exception):
    """Raised when an object does not exist."""

    pass


class HTTPException(BaseHTTPException):
    """Raised when an HTTP exception occurs."""

    errors: Optional[Dict[str, List[str]]] = None

    def __init__(self, status_code: int, detail: str, errors: Optional[Dict[str, List[str]]] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.errors = errors
