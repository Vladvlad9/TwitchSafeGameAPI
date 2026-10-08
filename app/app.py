from fastapi import FastAPI

from app import include_routers, cors_middleware
from app.openapi import TAGS_METADATA, DESCRIPTION
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
        openapi_tags=TAGS_METADATA
    )
    cors_middleware(app=app)
    include_routers(app=app)

    return app
