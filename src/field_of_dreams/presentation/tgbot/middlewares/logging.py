import logging
from typing import Callable
from field_of_dreams.infrastructure.tgbot import Middleware, TelegramBot

logger = logging.getLogger()


class LoggingMiddleware(Middleware):
    async def __call__(self, update, handler: Callable, bot: TelegramBot):
        logger.info(
            "New update in chat {}".format(update["message"]["chat"]["id"])
        )
        update = await handler(update, bot)
        return update
