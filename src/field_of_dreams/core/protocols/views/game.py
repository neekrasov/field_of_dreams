from typing import Protocol, Sequence

from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.player import Player


class GameView(Protocol):
    async def show_queue(
        self, chat_id: ChatID, queue: Sequence[Player]
    ) -> None:
        raise NotImplementedError

    async def notify_first_player_of_turn(
        self, chat_id: ChatID, player: Player
    ) -> None:
        raise NotImplementedError

    async def pin_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        raise NotImplementedError
