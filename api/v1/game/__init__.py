from fastapi import APIRouter
from .handlers import router

game = APIRouter(prefix="/game")
game.include_router(router)