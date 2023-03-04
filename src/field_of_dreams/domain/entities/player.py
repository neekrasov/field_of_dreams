import enum
import uuid
from typing import NewType, Optional
from dataclasses import dataclass
from datetime import datetime

from .game import GameID
from .user import UserID, User

PlayerID = NewType("PlayerID", uuid.UUID)


class PlayerState(enum.Enum):
    WINNER = "winner"
    LOSER = "loser"
    PLAYING = "playing"


@dataclass
class Player:
    game_id: GameID
    user_id: UserID
    score: int = 0
    state: PlayerState = PlayerState.PLAYING
    id: Optional[PlayerID] = None
    joined_at: Optional[datetime] = None
    user: Optional[User] = None
