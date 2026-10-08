from fastapi import FastAPI

from api import api

__all__ = ['include_routers']


def include_routers(app: FastAPI) -> None:
    app.include_router(router=api)
