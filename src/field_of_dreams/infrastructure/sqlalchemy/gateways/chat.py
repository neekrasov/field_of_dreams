from dataclasses import asdict

from field_of_dreams.domain.entities.chat import Chat
from field_of_dreams.application.protocols.gateways.chat import ChatGateway
from .base import SqlalchemyGateway
from ..models import Chat as ChatModel


class ChatGatewayImpl(SqlalchemyGateway, ChatGateway):
    async def add_chat(self, chat: Chat) -> None:
        self._session.add(ChatModel(**asdict(chat)))
        await self._try_flush()
