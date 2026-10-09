from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.game import GAME_EVENTS_CHANNEL, RedisGameStore

router = APIRouter(tags=['Game'])


class CreateGameRequest(BaseModel):
    code: Annotated[str, Field(min_length=1, max_length=128)]
    ttl_seconds: Annotated[int, Field(gt=0)] = 3600


def get_game_store(request: Request) -> RedisGameStore:
    return request.app.state.game_store


async def game_event_stream(request: Request) -> AsyncIterator[str]:
    pubsub = request.app.state.redis.pubsub()
    await pubsub.subscribe(GAME_EVENTS_CHANNEL)

    try:
        yield "retry: 3000\n\n"

        while not await request.is_disconnected():
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=15,
            )
            if message is None:
                yield ": keep-alive\n\n"
                continue

            yield f"event: game.won\ndata: {message['data']}\n\n"
    finally:
        await pubsub.unsubscribe(GAME_EVENTS_CHANNEL)
        await pubsub.aclose()


@router.post("/")
async def create_game(payload: CreateGameRequest, request: Request):
    game = await get_game_store(request).create_game(
        payload.code,
        ttl_seconds=payload.ttl_seconds,
    )
    return {
        "status": game.status,
        "winner": game.winner_name,
        "ttl_seconds": payload.ttl_seconds,
    }


@router.get("/")
async def get_game(request: Request):
    game_store = get_game_store(request)
    game = await game_store.get_game()
    if game is None:
        return {
            "status": "not_started",
            "winner": None,
            "ttl_seconds": None,
        }

    return {
        "status": game.status,
        "winner": game.winner_name,
        "ttl_seconds": await game_store.get_ttl(),
    }


@router.get("/events")
async def get_game_events(request: Request) -> StreamingResponse:
    return StreamingResponse(
        game_event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
