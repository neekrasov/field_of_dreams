from typing import Sequence
from sqlalchemy.sql import select

from field_of_dreams.domain.entities.game import GameID
from field_of_dreams.domain.entities.player import Player
from field_of_dreams.application.protocols.gateways.player import PlayerGateway
from .base import SqlalchemyGateway


class PlayerGatewayImpl(SqlalchemyGateway, PlayerGateway):
    async def add_player(self, player: Player):
        self._session.add(player)
        await self._try_flush()

    async def get_players(self, game_id: GameID) -> Sequence[Player]:
        stmt = select(Player).where(Player.game_id == game_id)  # type: ignore
        result = await self._session.execute(stmt)
        return result.scalars().all()
