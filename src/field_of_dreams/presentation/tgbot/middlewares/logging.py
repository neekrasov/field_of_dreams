import logging
from typing import Callable

from field_of_dreams.infrastructure.tgbot import Middleware, TelegramBot

logger = logging.getLogger()


class LoggingMiddleware(Middleware):
    def __init__(self, bot: TelegramBot):
        self._bot = bot

    async def __call__(self, update, handler: Callable):
        logger.info(
            "New update in chat {}".format(update["message"]["chat"]["id"])
        )
        update = await handler(update, self._bot)
        return update
