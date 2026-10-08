from fastapi import APIRouter
from .game import router as game_router

v1 = APIRouter(prefix="/v1")
v1.include_router(game_router)