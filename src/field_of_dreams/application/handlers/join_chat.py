from dataclasses import dataclass

from field_of_dreams.domain.entities.chat import ChatID, Chat
from ..common import Handler, UnitOfWork, GatewayError
from ..protocols.gateways.chat import ChatGateway


@dataclass(frozen=True)
class JoinToChatCommand:
    chat_id: ChatID
    chat_name: str


class JoinToChatHandler(Handler[JoinToChatCommand, None]):
    def __init__(self, chat_gateway: ChatGateway, uow: UnitOfWork):
        self._chat_gateway = chat_gateway
        self._uow = uow

    async def execute(self, command: JoinToChatCommand):
        async with self._uow.pipeline:
            try:
                await self._chat_gateway.add_chat(
                    Chat(id=command.chat_id, name=command.chat_name)
                )
            except GatewayError:
                pass
