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
    FINISHED = GameData(4)
