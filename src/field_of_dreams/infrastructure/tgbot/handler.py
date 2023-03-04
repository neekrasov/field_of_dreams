from typing import List, Callable, Type

from .protocols import Bot, Middleware, Filter


class UpdateHandler:
    def __init__(
        self,
        bot: Bot,
        filters: List[Type[Filter]],
        middlewares: List[Middleware],
        handler: Callable,
    ):
        self._filters = filters
        self._handler = handler
        self._middlewares = middlewares
        self._bot = bot

    async def handle(self, update):
        for middleware in self._middlewares:
            update = await middleware(update, self._handler)
        await self._handler(update, self._bot)

    @property
    def filters(self):
        return self._filters
