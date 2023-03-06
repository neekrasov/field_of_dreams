import traceback
import logging
from typing import List, Callable, Type, Dict, Awaitable

from .protocols import Bot, Middleware, Filter

logger = logging.getLogger()


class UpdateHandler:
    def __init__(
        self,
        bot: Bot,
        filters: List[Filter],
        middlewares: List[Middleware],
        handler: Callable[..., Awaitable],
        exc_handlers: Dict[Type[Exception], Callable[..., Awaitable]],
    ):
        self._filters = filters
        self._handler = handler
        self._middlewares = middlewares
        self._bot = bot
        self._exc_handlers = exc_handlers

    async def handle(self, update: dict):
        try:
            for middleware in self._middlewares:
                update = await middleware(update, self._handler)
            if update:
                await self._handler(update, self._bot)
        except Exception as e:
            exc_type = type(e)
            exc_handler = self._exc_handlers.get(exc_type, None)
            if exc_handler:
                await exc_handler(update=update, e=e, bot=self._bot)
            else:
                logger.info(traceback.format_exc())
                raise e

    @property
    def filters(self):
        return self._filters
