from typing import Dict

from field_of_dreams.domain.entities.player_turn import (
    PlayerTurn,
    PlayerTurnID,
)
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)


class InMemoryPlayerTurnGateway(PlayerTurnGateway):
    def __init__(self, player_turns: Dict[PlayerTurnID, PlayerTurn]):
        self._player_turns = player_turns

    async def add_player_turn(self, player_turn: PlayerTurn):
        player_turn.id = max(self._player_turns.keys(), default=0) + 1  # type: ignore # noqa
        self._player_turns[player_turn.id] = player_turn  # type: ignore
