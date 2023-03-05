from field_of_dreams.domain.entities.chat import Chat
from field_of_dreams.application.protocols.gateways.chat import ChatGateway
from .base import SqlalchemyGateway


class ChatGatewayImpl(SqlalchemyGateway, ChatGateway):
    async def add_chat(self, chat: Chat) -> None:
        self._session.add(chat)
        await self._try_flush()
