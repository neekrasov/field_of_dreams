import enum
import uuid
from typing import NewType, Optional
from dataclasses import dataclass
from datetime import datetime

from .game import GameID
from .user import UserID, User

PlayerID = NewType("PlayerID", uuid.UUID)


class PlayerState(enum.Enum):
    WAITING = "waiting"
    PROCESSING = "processing"


@dataclass
class Player:
    game_id: GameID
    user_id: UserID
    user: User
    is_active: bool
    score: int = 0
    state: PlayerState = PlayerState.WAITING
    id: Optional[PlayerID] = None
    joined_at: Optional[datetime] = None

    @property
    def username(self) -> str:
        return self.user.name

    def set_state(self, state: PlayerState) -> None:
        self.state = state

    def add_score(self, score: int) -> None:
        self.score += score

    def get_score(self) -> int:
        return self.score
