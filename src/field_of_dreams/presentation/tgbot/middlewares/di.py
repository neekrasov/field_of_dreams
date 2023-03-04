from typing import Callable, Awaitable
from di import Container, ScopeState
from di.executors import AsyncExecutor
from di.dependent import Dependent

from field_of_dreams.infrastructure.di import DIScope
from field_of_dreams.infrastructure.tgbot import Middleware, TelegramBot


class DIMiddleware(Middleware):
    def __init__(
        self, container: Container, di_state: ScopeState, bot: TelegramBot
    ) -> None:
        self._container = container
        self._di_state = di_state
        self._bot = bot

    async def __call__(
        self,
        update: dict,
        handler: Callable[..., Awaitable],
    ):
        async with self._container.enter_scope(
            DIScope.REQUEST, self._di_state
        ) as request_state:
            solved = self._container.solve(
                Dependent(handler, scope=DIScope.REQUEST),
                scopes=[DIScope.APP, DIScope.REQUEST],
            )
            return await solved.execute_async(
                AsyncExecutor(),
                request_state,
                values={
                    dict: update,
                    Callable[..., Awaitable]: handler,  # type: ignore
                    TelegramBot: self._bot,
                },
            )
