from typing import Protocol, Optional

from field_of_dreams.core.entities.chat import ChatID, Chat


class ChatGateway(Protocol):
    async def create_chat(self, chat_id: ChatID, chat_title: str) -> None:
        raise NotImplementedError

    async def get_chat_by_id(self, chat_id: ChatID) -> Optional[Chat]:
        raise NotImplementedError
