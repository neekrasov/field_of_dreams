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
    PREPARED = GameData(3)
    STARTED = GameData(4)
    PLAYER_CHOICE = GameData(5)
    WAIT_PLAYER_CHOICE = GameData(6)
    PLAYER_LETTER_TURN = GameData(7)
    PLAYER_WORD_TURN = GameData(8)
    FINISHED = GameData(9)
    PLUG = GameData(10)
