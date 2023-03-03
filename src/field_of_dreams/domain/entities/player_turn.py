import enum
from typing import Optional, NewType
from dataclasses import dataclass
from datetime import datetime

from .player import PlayerID

PlayerTurnID = NewType("PlayerTurnID", int)


class TurnState(enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"


@dataclass
class PlayerTurn:
    player_id: PlayerID
    id: Optional[PlayerTurnID] = None
    start_time: Optional[datetime] = None
    state: TurnState = TurnState.IN_PROGRESS
