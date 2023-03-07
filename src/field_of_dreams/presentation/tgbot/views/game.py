from typing import Sequence

from field_of_dreams.domain.entities.user import User
from field_of_dreams.domain.entities.player import Player
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.application.protocols.views.game import GameView
from field_of_dreams.infrastructure.tgbot.protocols import Bot


class GameViewImpl(GameView):
    def __init__(self, bot: Bot):
        self._bot = bot

    async def show_queue(self, chat_id: ChatID, queue: Sequence[Player]):
        players = " ".join(
            [
                player.get_username()
                for player in queue
            ]
        )
        await self._bot.send_message(chat_id, f"Текущая очередь: {players}")

    async def notify_first_player_of_turn(
        self, chat_id: ChatID, user: User
    ) -> None:
        await self._bot.send_message(
            chat_id, f"Первый пользователь: @{user.name}"
        )
