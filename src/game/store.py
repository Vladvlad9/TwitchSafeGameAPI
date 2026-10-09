import hashlib
import secrets
from datetime import UTC, datetime
from uuid import uuid4

from redis.asyncio import Redis

from src.game.models import GameState, GameStatus, GuessResult

__all__ = ["RedisGameStore"]


class RedisGameStore:
    _GAME_KEY = "twitch-game:active"

    _CREATE_GAME_SCRIPT = """
    redis.call('DEL', KEYS[1])
    redis.call('HSET', KEYS[1],
        'game_id', ARGV[1],
        'status', 'active',
        'code_hash', ARGV[2],
        'salt', ARGV[3],
        'attempts', '0',
        'started_at', ARGV[4]
    )
    return 1
    """

    _SUBMIT_GUESS_SCRIPT = """
    if redis.call('EXISTS', KEYS[1]) == 0 then
        return 0
    end

    if redis.call('HGET', KEYS[1], 'game_id') ~= ARGV[1] then
        return 0
    end

    if redis.call('HGET', KEYS[1], 'status') ~= 'active' then
        return 3
    end

    redis.call('HINCRBY', KEYS[1], 'attempts', 1)

    if redis.call('HGET', KEYS[1], 'code_hash') ~= ARGV[2] then
        return 1
    end

    redis.call('HSET', KEYS[1],
        'status', 'finished',
        'winner_user_id', ARGV[3],
        'winner_name', ARGV[4],
        'finished_at', ARGV[5]
    )
    return 2
    """

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def create_game(
        self,
        code: str,
    ) -> GameState:
        normalized_code = self._normalize_code(code)
        game_id = str(uuid4())
        salt = secrets.token_hex(16)
        started_at = datetime.now(UTC).isoformat()
        code_hash = self._hash_code(normalized_code, salt)

        created = await self._redis.eval(
            self._CREATE_GAME_SCRIPT,
            1,
            self._GAME_KEY,
            game_id,
            code_hash,
            salt,
            started_at,
        )
        if created != 1:
            raise RuntimeError("Could not create game")

        return GameState(
            game_id=game_id,
            status=GameStatus.ACTIVE,
            attempts=0,
            started_at=started_at,
        )

    async def get_game(self) -> GameState | None:
        data = await self._redis.hgetall(self._GAME_KEY)
        if not data:
            return None

        return GameState(
            game_id=data["game_id"],
            status=GameStatus(data["status"]),
            attempts=int(data.get("attempts", 0)),
            started_at=data["started_at"],
            winner_user_id=data.get("winner_user_id"),
            winner_name=data.get("winner_name"),
        )

    async def submit_guess(
        self,
        guess: str,
        *,
        user_id: str,
        user_name: str,
    ) -> GuessResult:
        game_data = await self._redis.hmget(
            self._GAME_KEY,
            "game_id",
            "salt",
        )
        game_id, salt = game_data
        if game_id is None or salt is None:
            return GuessResult.NO_ACTIVE_GAME

        guess_hash = self._hash_code(self._normalize_code(guess), salt)
        result = await self._redis.eval(
            self._SUBMIT_GUESS_SCRIPT,
            1,
            self._GAME_KEY,
            game_id,
            guess_hash,
            user_id,
            user_name,
            datetime.now(UTC).isoformat(),
        )

        return {
            0: GuessResult.NO_ACTIVE_GAME,
            1: GuessResult.INCORRECT,
            2: GuessResult.WON,
            3: GuessResult.FINISHED,
        }[result]

    async def delete_game(self) -> bool:
        return bool(await self._redis.delete(self._GAME_KEY))

    @staticmethod
    def _normalize_code(code: str) -> str:
        normalized = code.strip()
        if not normalized:
            raise ValueError("Code must not be empty")
        return normalized

    @staticmethod
    def _hash_code(code: str, salt: str) -> str:
        value = f"{salt}:{code}".encode()
        return hashlib.sha256(value).hexdigest()
