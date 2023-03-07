from dataclasses import dataclass

from ..entities.chat import ChatID
from ..common import Handler, UnitOfWork, GatewayError
from ..protocols.gateways.chat import ChatGateway


@dataclass(frozen=True)
class JoinToChatCommand:
    chat_id: ChatID
    chat_title: str


class JoinToChatHandler(Handler[JoinToChatCommand, None]):
    def __init__(self, chat_gateway: ChatGateway, uow: UnitOfWork):
        self._chat_gateway = chat_gateway
        self._uow = uow

    async def execute(self, command: JoinToChatCommand):
        async with self._uow.pipeline:
            try:
                await self._chat_gateway.create_chat(
                    command.chat_id, command.chat_title
                )
            except GatewayError:
                pass

        await self._uow.commit()
