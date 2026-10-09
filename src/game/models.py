from dataclasses import dataclass
from enum import StrEnum

__all__ = ["GameState", "GameStatus", "GuessResult"]


class GameStatus(StrEnum):
    ACTIVE = "active"
    FINISHED = "finished"


class GuessResult(StrEnum):
    NO_ACTIVE_GAME = "no_active_game"
    INCORRECT = "incorrect"
    WON = "won"
    FINISHED = "finished"


@dataclass(frozen=True, slots=True)
class GameState:
    game_id: str
    status: GameStatus
    attempts: int
    started_at: str
    winner_user_id: str | None = None
    winner_name: str | None = None
