import uuid
import enum
from typing import List, Optional, NewType, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import timedelta, datetime

from .chat import ChatID
from .word import WordID
from .user import UserID

if TYPE_CHECKING:
    from .player_turn import PlayerTurnID

GameID = NewType("GameID", uuid.UUID)


class GameState(enum.Enum):
    PREPARING = "preparing"
    STARTED = "started"
    FINISHED = "finished"


@dataclass
class Game:
    chat_id: ChatID
    word_id: WordID
    interval: timedelta
    author_id: UserID
    current_turn_id: Optional["PlayerTurnID"] = None

    state: GameState = GameState.PREPARING
    guessed_letters: List[str] = field(default_factory=list)
    failed_letters: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: Optional[GameID] = None

    def set_state(self, state: GameState):
        self.state = state

    @property
    def is_active(self) -> bool:
        return (
            self.state == GameState.STARTED
            or self.state == GameState.PREPARING
        )
