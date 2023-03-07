from dataclasses import asdict

from field_of_dreams.domain.entities.player_turn import PlayerTurn
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from .base import SqlalchemyGateway
from ..models import PlayerTurn as PlayerTurnModel


class PlayerTurnGatewayImpl(SqlalchemyGateway, PlayerTurnGateway):
    async def add_player_turn(self, player_turn: PlayerTurn) -> None:
        self._session.add(PlayerTurnModel(**asdict(player_turn)))
        await self._try_flush()
