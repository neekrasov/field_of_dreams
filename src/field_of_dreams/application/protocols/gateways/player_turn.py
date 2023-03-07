from typing import Protocol

from field_of_dreams.domain.entities.player_turn import PlayerTurnID
from field_of_dreams.domain.entities.player import PlayerID


class PlayerTurnGateway(Protocol):
    async def create_player_turn(self, player_id: PlayerID) -> PlayerTurnID:
        raise NotImplementedError
