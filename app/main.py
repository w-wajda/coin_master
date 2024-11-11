#!/usr/bin/env python
from logging.config import dictConfig

from app.infrastructure.app import initialize_app
from app.infrastructure.conf import settings
from app.infrastructure.logger import LogConfig


log_config = LogConfig().model_dump()
dictConfig(log_config)


app = initialize_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=log_config,
        proxy_headers=True,
    )