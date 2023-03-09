from typing import Sequence, Callable, Awaitable
from functools import partial

from field_of_dreams.core.entities.player import Player
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.protocols.views.game import GameView
from field_of_dreams.infrastructure.tgbot.protocols import Bot


class GameViewImpl(GameView):
    ad_msg = "Вопрос: {question}\nСлово: {word_mask}.\nБукв {length}"

    def __init__(self, bot: Bot):
        self._bot = bot

    async def show_queue(
        self, chat_id: ChatID, queue: Sequence[Player]
    ) -> None:
        players = " ".join(
            [
                f"\n{index+1}. {player.get_username()}"
                for index, player in enumerate(queue)
            ]
        )
        await self._bot.send_message(chat_id, f"Текущая очередь:{players}")

    async def notify_first_player_of_turn(
        self, chat_id: ChatID, player: Player
    ) -> None:
        await self._bot.send_message(
            chat_id, f"Первый пользователь: @{player.get_username()}"
        )

    async def send_and_pin_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        message = await self._bot.send_message(
            chat_id,
            self.ad_msg.format(
                question=question, word_mask=word_mask, length=len(word_mask)
            ),
        )
        await self._bot.pin_message(chat_id, message.message_id)

    async def update_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        part_func = partial(
            self._bot.edit_message,
            text=self.ad_msg.format(
                question=question,
                word_mask=word_mask,
                length=len(word_mask),
            ),
        )
        await self._edit_pin(chat_id, part_func)

    async def unpin_word_mask(self, chat_id: ChatID) -> None:
        await self._edit_pin(chat_id, self._bot.unpin_message)

    async def _edit_pin(
        self, chat_id: ChatID, part_func: Callable[..., Awaitable]
    ) -> None:
        bot = await self._bot.get_me()
        chat = await self._bot.get_chat(chat_id)
        if message := chat.pinned_message:
            if user := message.from_user:
                if user.username == bot.username:
                    await part_func(
                        chat_id=chat_id, message_id=message.message_id
                    )

    async def correct_letter(
        self,
        chat_id: ChatID,
        letter: str,
        count: int,
        username: str,
        score_per_turn: int,
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username} угадал букву '{letter}'!\n"
                f"Начислено баллов за ход: {score_per_turn}.\n"
                f"Количество открытых позиций: {count}."
            ),
        )

    async def wrong_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=f"@{username} буква '{letter}' не встречается в слове :(",
        )

    async def already_guessed_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username} букву '{letter}' уже угадал другой игрок. \n"
                "Будьте внимательнее!"
            ),
        )

    async def winner_letter(
        self,
        chat_id: ChatID,
        letter: str,
        username: str,
        count: int,
        score_per_turn: int,
        total_score: int,
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username} угадал последнюю букву '{letter}'!\n"
                f"Начислено баллов за ход: {score_per_turn}.\n"
                f"Буква встречалась {count} раз.\n"
                f"Всего набрано баллов за игру: {total_score}."
            ),
        )

    async def notify_of_win_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
        score_per_turn: int,
        total_score: int,
    ):
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username} угадал слово '{word}'!\n"
                f"Начислено баллов за ход: {score_per_turn}.\n"
                f"Всего набрано баллов за игру: {total_score}."
            ),
        )

    async def notify_loss_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
    ):
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username}, к сожалению '{word}'"
                "не является загаданным словом :(\n"
                "И ты выбываешь из игры,"
                "не расстраивайся, в следующий раз обязательно получиться!"
            ),
        )
