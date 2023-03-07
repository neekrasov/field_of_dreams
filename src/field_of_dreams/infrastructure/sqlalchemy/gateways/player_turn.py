from field_of_dreams.domain.entities.player_turn import PlayerTurnID
from field_of_dreams.domain.entities.player import PlayerID
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from .base import SqlalchemyGateway
from ..models import PlayerTurn as PlayerTurnModel


class PlayerTurnGatewayImpl(SqlalchemyGateway, PlayerTurnGateway):
    async def create_player_turn(self, player_id: PlayerID) -> PlayerTurnID:
        db_player_turn = PlayerTurnModel(player_id=player_id)
        self._session.add(db_player_turn)
        await self._try_flush()
        return PlayerTurnID(db_player_turn.id)
