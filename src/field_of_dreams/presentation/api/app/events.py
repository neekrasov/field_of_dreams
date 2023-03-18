import logging
from di import ScopeState

from field_of_dreams.core.common import ApplicationException
from field_of_dreams.infrastructure.di import DIScope, DIContainer
from field_of_dreams.core.handlers.create_admin import (
    CreateAdminCommand,
    CreateAdminHandler,
)

logger = logging.getLogger()


async def create_admin(
    container: DIContainer, state: ScopeState, email: str, raw_password: str
) -> None:
    async with container.enter_scope(DIScope.REQUEST, state) as request_state:
        handler = await container.execute(
            handler=CreateAdminHandler,
            state=request_state,
            scope=DIScope.REQUEST
        )
        try:
            await handler.execute(CreateAdminCommand(email, raw_password))
        except ApplicationException as e:
            logger.info(e.message)
