import uuid
import enum
from typing import List, Optional, NewType, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import timedelta, datetime

from .chat import ChatID
from .word import WordID, Word
from .user import UserID

if TYPE_CHECKING:
    from .player import PlayerID, Player

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

    state: GameState = GameState.CREATED
    cur_player_id: Optional["PlayerID"] = None
    cur_player: Optional["Player"] = None
    guessed_letters: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    id: Optional[GameID] = None

    def set_state(self, state: GameState):
        self.state = state

    def set_current_player(self, player_id: "PlayerID"):
        self.cur_player_id = player_id

    @property
    def is_started(self) -> bool:
        return self.state == GameState.STARTED

    @property
    def is_created(self) -> bool:
        return self.state == GameState.CREATED

    def add_guessed_letter(self, letter: str):
        self.guessed_letters.append(letter)

    def check_already_guessed_letter(self, letter: str) -> bool:
        if letter in self.guessed_letters:
            return True
        return False

    def finish(self) -> None:
        self.state = GameState.FINISHED
        self.end_time = datetime.utcnow()

    def is_finished(self) -> bool:
        return self.state == GameState.FINISHED

    def check_user_queue(self, user_id: UserID) -> bool:
        if self.cur_player:
            return self.cur_player.user_id == user_id
        return False

    def set_next_player(self, next_player: "Player") -> None:
        self.cur_player = next_player
        self.cur_player_id = next_player.id
