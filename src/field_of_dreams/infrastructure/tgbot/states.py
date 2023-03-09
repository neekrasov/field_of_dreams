from typing import Optional, Any
from dataclasses import dataclass
import enum


@dataclass
class GameData:
    filter_: int
    data: Optional[Any] = None

    def set_data(self, data: Any) -> None:
        self.data = data


class GameState(enum.Enum):
    CREATED = GameData(1)
    PREPARING = GameData(2)
    STARTED = GameData(3)
    PLAYER_CHOICE = GameData(4)
    WAIT_PLAYER_CHOICE = GameData(5)
    PLAYER_LETTER_TURN = GameData(6)
    PLAYER_WORD_TURN = GameData(7)
    FINISHED = GameData(8)
