from typing import Callable, Awaitable
from di import ScopeState

from field_of_dreams.infrastructure.di import DIScope, DIContainer
from field_of_dreams.infrastructure.tgbot import Middleware, Bot
from field_of_dreams.infrastructure.tgbot.types import Update


class DIMiddleware(Middleware):
    def __init__(
        self, container: DIContainer, di_state: ScopeState, bot: Bot
    ) -> None:
        self._container = container
        self._di_state = di_state
        self._bot = bot

    async def __call__(
        self,
        update: Update,
        handler: Callable[..., Awaitable],
    ):
        async with self._container.enter_scope(
            DIScope.REQUEST, self._di_state
        ) as request_state:
            return await self._container.execute(
                handler,
                request_state,
                DIScope.REQUEST,
                values={Update: update},
            )
