from typing import Protocol, List

from field_of_dreams.domain.entities.player import Player
from field_of_dreams.domain.entities.chat import ChatID


class GameView(Protocol):
    async def send_queue(self, chat_id: ChatID, queue: List[Player]) -> None:
        raise NotImplementedError

    async def notify_first_player_of_turn(
        self, chat_id: ChatID, player: Player
    ) -> None:
        raise NotImplementedError
