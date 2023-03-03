import enum
import uuid
from typing import NewType, Optional
from dataclasses import dataclass

from .game import GameID
from .user import UserID

PlayerID = NewType("PlayerID", uuid.UUID)


class PlayerState(enum.Enum):
    WINNER = "WINNER"
    LOSER = "LOSER"
    PLAYING = "PLAYING"


@dataclass
class Player:
    game_id: GameID
    user_id: UserID
    score: int = 0
    state: PlayerState = PlayerState.PLAYING
    id: Optional[PlayerID] = None
