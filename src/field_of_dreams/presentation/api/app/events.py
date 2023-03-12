import logging
from di.executors import AsyncExecutor
from di import Container, ScopeState
from di.dependent import Dependent

from field_of_dreams.core.common import ApplicationException
from field_of_dreams.infrastructure.di import DIScope
from field_of_dreams.core.handlers.create_admin import (
    CreateAdminCommand,
    CreateAdminHandler,
)

logger = logging.getLogger()


async def create_admin(
    container: Container, state: ScopeState, email: str, raw_password: str
) -> None:
    executor = AsyncExecutor()
    handler_solved = container.solve(
        Dependent(CreateAdminHandler, scope=DIScope.REQUEST),
        [DIScope.APP, DIScope.REQUEST],
    )
    async with container.enter_scope(DIScope.REQUEST, state) as request_state:
        handler = await handler_solved.execute_async(executor, request_state)
        try:
            await handler.execute(CreateAdminCommand(email, raw_password))
        except ApplicationException as e:
            logger.info(e.message)
