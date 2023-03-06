from typing import Optional
from sqlalchemy.sql import select, and_, or_

from field_of_dreams.domain.entities.game import Game, GameState
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.application.protocols.gateways.game import GameGateway
from .base import SqlalchemyGateway


class GameGatewayImpl(SqlalchemyGateway, GameGateway):
    async def add_game(self, game: Game):
        self._session.add(game)
        await self._try_flush()

    async def get_current_game(self, chat_id: ChatID) -> Optional[Game]:
        stmt = select(Game).where(
            and_(
                Game.chat_id == chat_id,  # type: ignore
                or_(
                    Game.state == GameState.STARTED,  # type: ignore
                    Game.state == GameState.PREPARING,  # type: ignore
                ),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def delete_game(self, game: Game):
        await self._session.delete(game)
