from fastapi import FastAPI

from app import include_routers, cors_middleware
from settings import settings

__all__ = ['application']


def application() -> FastAPI:
    app = FastAPI(
        title=settings.APP.PROJECT_NAME,
        version=settings.APP.VERSION,
    )
    include_routers(app=app)
    cors_middleware(app=app)
    return app
