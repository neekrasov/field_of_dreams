from typing import Optional, cast
from dataclasses import asdict
from sqlalchemy.sql import select, and_, or_

from field_of_dreams.domain.entities.game import Game, GameState
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.application.protocols.gateways.game import GameGateway
from .base import SqlalchemyGateway
from ..models import Game as GameModel


class GameGatewayImpl(SqlalchemyGateway, GameGateway):
    async def add_game(self, game: Game):
        self._session.add(GameModel(**asdict(game)))
        await self._try_flush()

    async def get_current_game(self, chat_id: ChatID) -> Optional[Game]:
        stmt = select(GameModel).where(
            and_(
                GameModel.chat_id == chat_id,
                or_(
                    GameModel.state == GameState.STARTED,
                    GameModel.state == GameState.PREPARING,
                    GameModel.state == GameState.CREATED,
                ),
            )
        )
        result = await self._session.execute(stmt)
        return cast(Game, result.scalars().first())

    async def delete_game(self, game: Game):
        await self._session.delete(game)
