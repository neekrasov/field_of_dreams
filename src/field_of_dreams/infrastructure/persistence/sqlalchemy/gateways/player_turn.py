from field_of_dreams.domain.entities.player_turn import PlayerTurn
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from .base import SqlalchemyGateway


class PlayerTurnGatewayImpl(SqlalchemyGateway, PlayerTurnGateway):
    async def add_player_turn(self, player_turn: PlayerTurn) -> None:
        self._session.add(chat)
        await self._try_flush()
