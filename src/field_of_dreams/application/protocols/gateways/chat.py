from typing import Protocol

from field_of_dreams.domain.entities.chat import Chat


class ChatGateway(Protocol):
    async def add_chat(self, chat: Chat) -> None:
        raise NotImplementedError
