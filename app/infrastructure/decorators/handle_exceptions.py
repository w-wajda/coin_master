from functools import wraps

from starlette.responses import JSONResponse

from app.domain.exceptions import HTTPException


def handle_exceptions(*exceptions):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as exc:
                if isinstance(exc, HTTPException):
                    content = {
                        "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
                        "title": exc.detail,
                        "status": exc.status_code,
                    }
                    if exc.errors:
                        content["errors"] = exc.errors
                    return JSONResponse(status_code=exc.status_code, content=content)
                raise

        return wrapper

    return decorator
