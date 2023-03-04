import logging
from typing import Callable

from field_of_dreams.infrastructure.tgbot import Middleware, Bot
from field_of_dreams.application.common.exception import ApplicationException

logger = logging.getLogger()


class ExceptionsMiddleware(Middleware):
    def __init__(self, bot: Bot):
        self._bot = bot

    async def __call__(self, update, handler: Callable):
        try:
            update = await handler(update, self._bot)
        except ApplicationException as e:
            chat_id = update["message"]["chat"]["id"]
            logger.exception(
                "Exception in chat {}: {}",
                chat_id,
                e.message,
            )
            await self._bot.send_message(chat_id, e.message)
        return update
