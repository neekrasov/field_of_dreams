from typing import Protocol

from field_of_dreams.domain.entities.user import User
from field_of_dreams.domain.entities.chat import ChatID


class GameView(Protocol):
    async def notify_first_player_of_turn(
        self, chat_id: ChatID, user: User
    ) -> None:
        raise NotImplementedError
