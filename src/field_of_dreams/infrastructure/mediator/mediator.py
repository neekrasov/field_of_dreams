from typing import Any, Dict

from field_of_dreams.core.common.handler import Handler, InputType
from field_of_dreams.core.common.mediator import (
    Mediator,
    CommandNotFoundException,
)


class MediatorImpl(Mediator):
    def __init__(self) -> None:
        self._handlers: Dict[Any, Handler] = {}

    async def send(self, command: InputType) -> Any:
        try:
            handler = self._handlers[type(command)]
        except KeyError:
            raise CommandNotFoundException(
                f"Command {command.__class__} not binded"
            )
        return await handler.execute(command)

    def bind(self, command: InputType, handler: Handler):
        self._handlers[command] = handler
