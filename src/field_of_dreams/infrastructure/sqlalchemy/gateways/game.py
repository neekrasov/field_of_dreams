from typing import Optional
from datetime import timedelta
from sqlalchemy.sql import select, and_, or_, update
from sqlalchemy.orm import joinedload

from field_of_dreams.core.entities.game import Game, GameState, GameID
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.word import WordID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.protocols.gateways.game import GameGateway
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
        stmt = (
            select(GameModel)
            .where(
                and_(
                    GameModel.chat_id == chat_id,
                    or_(
                        GameModel.state == GameState.STARTED,
                        GameModel.state == GameState.PREPARING,
                        GameModel.state == GameState.CREATED,
                    ),
                )
            )
            .options(joinedload("*"))
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def update_game(self, game: Game) -> None:
        await self._session.execute(
            update(GameModel)
            .where(GameModel.chat_id == game.chat_id)
            .values(
                chat_id=game.chat_id,
                word_id=game.word_id,
                interval=game.interval,
                author_id=game.author_id,
                state=game.state,
                cur_player_id=game.cur_player_id,
                guessed_letters=game.guessed_letters,
                start_time=game.start_time,
            )
        )

    async def delete_game(self, game: Game):
        await self._session.delete(game)
