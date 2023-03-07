import uuid
import enum
from typing import List, Optional, NewType, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import timedelta, datetime

from .chat import ChatID
from .word import WordID, Word
from .user import UserID

if TYPE_CHECKING:
    from .player_turn import PlayerTurnID

GameID = NewType("GameID", uuid.UUID)


class GameState(enum.Enum):
    CREATED = "created"
    PREPARING = "preparing"
    STARTED = "started"
    FINISHED = "finished"


@dataclass
class Game:
    chat_id: ChatID
    word_id: WordID
    interval: timedelta
    author_id: UserID
    word: Word

    current_turn_id: Optional["PlayerTurnID"] = None
    state: GameState = GameState.CREATED
    guessed_letters: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: Optional[GameID] = None

    def set_state(self, state: GameState):
        self.state = state

    def set_turn(self, turn_id: "PlayerTurnID"):
        self.current_turn_id = turn_id

    @property
    def is_active(self) -> bool:
        return (
            self.state == GameState.STARTED
            or self.state == GameState.PREPARING
        )

    @property
    def is_started(self) -> bool:
        return self.state == GameState.STARTED

    @property
    def is_created(self) -> bool:
        return self.state == GameState.CREATED
