from typing import Optional, cast
from datetime import timedelta
from sqlalchemy.sql import select, and_, or_
from sqlalchemy.orm import joinedload

from field_of_dreams.domain.entities.game import Game, GameState, GameID
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.word import WordID
from field_of_dreams.domain.entities.user import UserID
from field_of_dreams.application.protocols.gateways.game import GameGateway
from .base import SqlalchemyGateway
from ..models import Game as GameModel


class GameGatewayImpl(SqlalchemyGateway, GameGateway):
    async def create_game(
        self,
        chat_id: ChatID,
        word_id: WordID,
        interval: timedelta,
        author_id: UserID,
    ) -> GameID:
        db_game = GameModel(
            chat_id=chat_id,
            word_id=word_id,
            interval=interval,
            author_id=author_id,
        )
        self._session.add(db_game)
        await self._try_flush()
        return GameID(db_game.id)

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
        ).options(joinedload(GameModel.word))
        result = await self._session.execute(stmt)
        return cast(Game, result.scalars().first())

    async def delete_game(self, game: Game):
        await self._session.delete(game)
