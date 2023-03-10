from typing import Sequence, Optional
from sqlalchemy.sql import select, or_, and_, update
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
            .where(
                PlayerModel.game_id == game_id,
                PlayerModel.is_active == True,  # noqa
            )
            .options(selectinload(PlayerModel.user))
        )
        result = await self._session.execute(stmt)
        players = result.scalars().all()
        return players

    async def get_next_player(
        self, player: Player, game_id: GameID
    ) -> Optional[Player]:
        stmt = (
            select(PlayerModel)
            .options(selectinload(PlayerModel.user))
            .where(
                and_(
                    PlayerModel.id != player.id,
                    PlayerModel.game_id == game_id,
                    PlayerModel.is_active == True,  # noqa
                    or_(
                        PlayerModel.joined_at > player.joined_at,
                        and_(
                            PlayerModel.joined_at == player.joined_at,
                            PlayerModel.id > player.id,
                        ),
                    ),
                )
            )
            .order_by(PlayerModel.id, PlayerModel.joined_at)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        next_player = result.scalars().first()

        if not next_player:
            stmt = (
                select(PlayerModel)
                .where(
                    PlayerModel.user_id != player.user_id,
                    PlayerModel.game_id == game_id,
                    PlayerModel.is_active == True,  # noqa
                )
                .order_by(PlayerModel.id, PlayerModel.joined_at)
                .limit(1)
            )
            result = await self._session.execute(stmt)
            next_player = result.scalars().first()

        return next_player

    async def update_player(self, player: Player) -> None:
        await self._session.execute(
            update(PlayerModel)
            .where(PlayerModel.id == player.id)
            .values(
                is_active=player.is_active,
                score=player.score,
                state=player.state,
            )
        )
