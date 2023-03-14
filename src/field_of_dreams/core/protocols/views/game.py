from typing import Protocol, Sequence

from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.player import Player
from field_of_dreams.core.entities.user_stats import UserStats


class GameView(Protocol):
    async def show_queue(
        self, chat_id: ChatID, queue: Sequence[Player]
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

    async def notify_correct_letter(
        self,
        chat_id: ChatID,
        letter: str,
        count: int,
        username: str,
        score_per_turn: int,
    ) -> None:
        raise NotImplementedError

    async def notify_wrong_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        raise NotImplementedError

    async def already_guessed_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        raise NotImplementedError

    async def notify_winner_letter(
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
    ) -> None:
        raise NotImplementedError

    async def notify_loss_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
    ) -> None:
        raise NotImplementedError

    async def notify_empty_stats(self, chat_id: ChatID) -> None:
        raise NotImplementedError

    async def show_stats(
        self, chat_id: ChatID, stats: Sequence[UserStats]
    ) -> None:
        raise NotImplementedError

    async def notify_empty_stats_chat_not_exists(self, chat_id: ChatID):
        raise NotImplementedError

    async def notify_dont_support_numeric(
        self, chat_id: ChatID, username: str
    ) -> None:
        raise NotImplementedError

    async def notify_dont_support_punctuation(
        self, chat_id: ChatID, username: str
    ) -> None:
        raise NotImplementedError
