from typing import Annotated

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.game import RedisGameStore

router = APIRouter(tags=['Game'])


class CreateGameRequest(BaseModel):
    code: Annotated[str, Field(min_length=1, max_length=128)]


def get_game_store(request: Request) -> RedisGameStore:
    return request.app.state.game_store


@router.post("/")
async def create_game(payload: CreateGameRequest, request: Request):
    game = await get_game_store(request).create_game(payload.code)
    return {
        "status": game.status,
        "winner": game.winner_name,
    }


@router.get("/")
async def get_game(request: Request):
    game = await get_game_store(request).get_game()
    if game is None:
        return {
            "status": "not_started",
            "winner": None,
        }

    return {
        "status": game.status,
        "winner": game.winner_name,
    }
