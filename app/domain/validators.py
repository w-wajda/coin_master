from functools import wraps
from typing import Callable


def validate_true(message: str) -> Callable[[bool], bool]:
    def validator(value: bool) -> bool:
        if not value:
            raise ValueError(message)
        return value

    @wraps(validator)
    def wrapped_validator(value: bool) -> bool:
        return validator(value)

    return wrapped_validator
