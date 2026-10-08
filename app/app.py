from fastapi import FastAPI

from app.lifespan import lifespan
from app.middleware.cors_middleware import cors_middleware
from app.openapi import TAGS_METADATA, DESCRIPTION
from app.routers.setup import include_routers
from settings import settings

__all__ = ["get_application"]


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP.PROJECT_NAME,
        version=settings.APP.VERSION,
        description=DESCRIPTION,
        contact={
            "name": "Paulechka Uladzislau",
        },
        openapi_tags=TAGS_METADATA,
        lifespan=lifespan,
    )
    cors_middleware(app=app)
    include_routers(app=app)

    return app
