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

    async def send_and_pin_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        raise NotImplementedError

    async def update_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        raise NotImplementedError

    async def unpin_word_mask(self, chat_id: ChatID) -> None:
        raise NotImplementedError

    async def correct_letter(
        self,
        chat_id: ChatID,
        letter: str,
        count: int,
        username: str,
        score_per_turn: int,
    ) -> None:
        raise NotImplementedError

    async def wrong_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        raise NotImplementedError

    async def already_guessed_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        raise NotImplementedError

    async def winner_letter(
        self,
        chat_id: ChatID,
        letter: str,
        username: str,
        count: int,
        score_per_turn: int,
        total_score: int,
    ) -> None:
        raise NotImplementedError

    async def notify_of_win_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
        score_per_turn: int,
        total_score: int,
    ):
        raise NotImplementedError

    async def notify_loss_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
    ):
        raise NotImplementedError
