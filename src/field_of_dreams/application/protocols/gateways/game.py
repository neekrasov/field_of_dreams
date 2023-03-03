from typing import Protocol, Optional

from field_of_dreams.domain.entities.game import Game
from field_of_dreams.domain.entities.chat import ChatID


class GameGateway(Protocol):
    async def add_game(self, game: Game):
        raise NotImplementedError

    async def get_current_game(self, chat_id: ChatID) -> Optional[Game]:
        raise NotImplementedError
