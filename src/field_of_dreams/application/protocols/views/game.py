from typing import Protocol, Sequence

from field_of_dreams.domain.entities.user import User
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.player import Player


class GameView(Protocol):
    async def show_queue(self, chat_id: ChatID, queue: Sequence[Player]):
        raise NotImplementedError

    async def notify_first_player_of_turn(
        self, chat_id: ChatID, user: User
    ) -> None:
        raise NotImplementedError
