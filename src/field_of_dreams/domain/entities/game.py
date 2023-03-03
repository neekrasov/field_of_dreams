import uuid
import enum
from typing import List, Optional, NewType, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import timedelta, datetime

from .chat import ChatID
from .word import WordID

if TYPE_CHECKING:
    from .player import PlayerID
    from .player_turn import PlayerTurnID

GameID = NewType("GameID", uuid.UUID)


class GameStatus(enum.Enum):
    PREPARING = "preparing"
    STARTED = "started"
    FINISHED = "finished"


@dataclass
class Game:
    chat_id: ChatID
    word_id: WordID
    interval: timedelta
    author: "PlayerID"
    current_turn_id: Optional["PlayerTurnID"] = None

    game_status: GameStatus = GameStatus.PREPARING
    guessed_letters: List[str] = field(default_factory=list)
    failed_letters: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: Optional[GameID] = None

    def set_status(self, game_status: GameStatus):
        self.game_status = game_status

    @property
    def is_active(self) -> bool:
        return (
            self.game_status == GameStatus.STARTED
            or self.game_status == GameStatus.PREPARING
        )
