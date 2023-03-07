from typing import Sequence, cast
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload

from field_of_dreams.core.entities.game import GameID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.entities.player import Player
from field_of_dreams.core.protocols.gateways.player import PlayerGateway
from .base import SqlalchemyGateway
from ..models import Player as PlayerModel


class PlayerGatewayImpl(SqlalchemyGateway, PlayerGateway):
    async def create_player(self, game_id: GameID, user_id: UserID):
        db_player = PlayerModel(game_id=game_id, user_id=user_id)
        self._session.add(db_player)
        await self._try_flush()

    async def get_players(self, game_id: GameID) -> Sequence[Player]:
        stmt = (
            select(PlayerModel)
            .where(PlayerModel.game_id == game_id)
            .options(selectinload(PlayerModel.user))
        )
        result = await self._session.execute(stmt)
        players = result.scalars().all()
        return cast(Sequence[Player], players)
