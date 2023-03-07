from typing import Dict

from field_of_dreams.core.entities.chat import Chat, ChatID
from field_of_dreams.core.protocols.gateways.chat import ChatGateway
from field_of_dreams.core.common import GatewayError


class InMemoryChatGateway(ChatGateway):
    def __init__(self, chats: Dict[ChatID, Chat]):
        self._chats = chats

    async def add_chat(self, chat: Chat) -> None:
        if chat.id not in self._chats:
            self._chats[chat.id] = chat
        else:
            raise GatewayError(f"Chat with id {chat.id} already exists")
