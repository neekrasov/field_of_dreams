from typing import Sequence, Callable, Awaitable
from functools import partial

from field_of_dreams.core.entities.player import Player
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user_stats import UserStats
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
                f"\n{index+1}. {player.username}"
                for index, player in enumerate(queue)
            ]
        )
        await self._bot.send_message(chat_id, f"Текущая очередь 👀:{players}")

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

    async def notify_correct_letter(
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
                f"🎯 @{username} угадал(а) букву '{letter}'!\n"
                f"🫰 Начислено баллов за ход: {score_per_turn}.\n"
                f"👀 Количество открытых позиций: {count}."
            ),
        )

    async def notify_wrong_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=f"🤔 @{username} буква '{letter}' не встречается в слове :(",
        )

    async def already_guessed_letter(
        self, chat_id: ChatID, letter: str, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"🥱 @{username} букву '{letter}' уже угадал другой игрок. \n"
                "Будьте внимательнее!"
            ),
        )

    async def notify_winner_letter(
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
                f"🥳 @{username} угадал(а) последнюю букву '{letter}'!\n"
                f"🫰 Начислено баллов за ход: {score_per_turn}.\n"
                f"👀 Буква встречалась {count} раз.\n"
                f"📈 Всего набрано баллов за игру: {total_score}."
            ),
        )

    async def notify_of_win_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
        score_per_turn: int,
        total_score: int,
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"🥳 @{username} угадал(а) слово '{word}'!\n"
                f"🫰 Начислено баллов за ход: {score_per_turn}.\n"
                f"📈 Всего набрано баллов за игру: {total_score}."
            ),
        )

    async def notify_loss_word(
        self,
        chat_id: ChatID,
        word: str,
        username: str,
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"😔 @{username}, к сожалению '{word}' "
                "не является загаданным словом :(\n"
                "🗣 Ты выбываешь из игры. "
                "Не расстраивайся, в следующий раз "
                "обязательно получится угадать!"
            ),
        )

    async def notify_empty_stats(self, chat_id: ChatID) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                "В этом чате не заканчивалась ещё ни одна игра 🫤 \n"
                "Начните игру! /game"
            ),
        )

    async def show_stats(
        self, chat_id: ChatID, stats: Sequence[UserStats]
    ) -> None:
        statistics = " ".join(
            [
                (
                    f"\n{index+1}. {stat.user.name} "
                    f"побед: {stat.wins} очков: {stat.total_score} "
                    f"игр: {stat.count_games}"
                )
                for index, stat in enumerate(stats)
            ]
        )
        await self._bot.send_message(
            chat_id, text=f"📈 Топ игроков:{statistics}"
        )

    async def notify_empty_stats_chat_not_exists(self, chat_id: ChatID):
        await self._bot.send_message(
            chat_id,
            text=(
                "Статистики пока что нет🫤"
                "\nДля начала познакомьтесь со мной - /start"
                "\nИ начите игру - /game"
            ),
        )

    async def notify_dont_support_numeric(
        self, chat_id: ChatID, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id, text=(f"@{username} слова не могут состоять из чисел 🙄")
        )

    async def notify_dont_support_punctuation(
        self, chat_id: ChatID, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"@{username} слова не могут состоять из знаков пунктуации 🙄"
            ),
        )

    async def notify_user_stats_not_found(
        self, chat_id: ChatID, username: str
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"{username}, пока что у тебя нет статистики 🙃\nЧтобы она"
                " появилась тебе нужно присоединится к 1 игре."
            ),
        )

    async def show_user_stats(
        self, chat_id: ChatID, username: str, stats: UserStats
    ) -> None:
        await self._bot.send_message(
            chat_id,
            text=(
                f"😋Статистика по пользователю - {username}"
                f"\n🎯Побед: {stats.wins}"
                f"\n🫰Очков: {stats.total_score}"
                f"\n⚔Игр: {stats.count_games}"
            ),
        )
