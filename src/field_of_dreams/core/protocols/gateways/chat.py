from typing import Protocol

from field_of_dreams.core.entities.chat import ChatID


class ChatGateway(Protocol):
    async def create_chat(self, chat_id: ChatID, chat_title: str) -> None:
        raise NotImplementedError
