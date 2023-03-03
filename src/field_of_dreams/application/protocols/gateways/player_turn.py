from typing import Protocol

from field_of_dreams.domain.entities.player_turn import PlayerTurn


class PlayerTurnGateway(Protocol):
    async def add_player_turn(self, player_turn: PlayerTurn) -> None:
        raise NotImplementedError
