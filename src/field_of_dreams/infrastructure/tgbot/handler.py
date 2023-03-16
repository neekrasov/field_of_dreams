import logging
from typing import List, Callable, Type, Dict, Awaitable

from .protocols import Bot, Middleware, Filter, Storage
from .types import Update

logger = logging.getLogger()


class UpdateHandler:
    def __init__(
        self,
        bot: Bot,
        filters: List[Filter],
        handler: Callable[..., Awaitable],
        middlewares: List[Middleware],
        storage: Storage,
        exc_handlers: Dict[Type[Exception], Callable[..., Awaitable]],
    ):
        self._filters = filters
        self._handler = handler
        self._middlewares = middlewares
        self._bot = bot
        self._exc_handlers = exc_handlers
        self._storage = storage

    async def handle(self, update: Update):
        try:
            for middleware in self._middlewares:
                handler = await middleware(update, self._handler)
                if handler:
                    self._handler = handler
        except Exception as e:
            exc_handler = self._exc_handlers.get(type(e), None)
            if exc_handler:
                await exc_handler(
                    update=update, e=e, bot=self._bot, storage=self._storage
                )
            else:
                logger.exception(e)
                raise e

    @property
    def filters(self):
        return self._filters
