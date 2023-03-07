from typing import Protocol, Optional
from datetime import timedelta

from field_of_dreams.domain.entities.game import Game, GameID
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.word import WordID
from field_of_dreams.domain.entities.user import UserID


class GameGateway(Protocol):
    async def create_game(
        self,
        chat_id: ChatID,
        word_id: WordID,
        interval: timedelta,
        author_id: UserID,
    ) -> GameID:
        raise NotImplementedError

    async def get_current_game(self, chat_id: ChatID) -> Optional[Game]:
        raise NotImplementedError

    async def delete_game(self, game: Game) -> None:
        raise NotImplementedError
