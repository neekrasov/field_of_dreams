from typing import Sequence

from field_of_dreams.core.entities.player import Player
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.protocols.views.game import GameView
from field_of_dreams.infrastructure.tgbot.protocols import Bot


class GameViewImpl(GameView):
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

    async def pin_word_mask(
        self, chat_id: ChatID, word_mask: str, question: str
    ) -> None:
        ad_msg = f"Вопрос: {question} \n" f"Слово: {word_mask}"
        chat = await self._bot.get_chat(chat_id)
        bot = await self._bot.get_me()
        if message := chat.pinned_message:  # type: ignore
            if message.from_user.username == bot.username:  # type: ignore # noqa
                await self._bot.edit_message(
                    chat_id, message.message_id, ad_msg  # type: ignore
                )
            else:
                await self._send_and_pin(chat_id, ad_msg)
        else:
            await self._send_and_pin(chat_id, ad_msg)

    async def _send_and_pin(self, chat_id: ChatID, message: str) -> None:
        message = await self._bot.send_message(chat_id, message)  # type: ignore # noqa
        await self._bot.pin_message(chat_id, message.message_id)  # type: ignore # noqa

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
