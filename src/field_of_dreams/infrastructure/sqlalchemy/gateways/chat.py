from typing import Optional
from sqlalchemy.sql import select

from field_of_dreams.core.entities.chat import ChatID, Chat
from field_of_dreams.core.protocols.gateways.chat import ChatGateway
from .base import SqlalchemyGateway
from ..models import Chat as ChatModel


class ChatGatewayImpl(SqlalchemyGateway, ChatGateway):
    async def create_chat(self, chat_id: ChatID, chat_title: str) -> None:
        db_chat = ChatModel(id=chat_id, title=chat_title)
        self._session.add(db_chat)
        await self._try_flush()

    async def get_chat_by_id(self, chat_id: ChatID) -> Optional[Chat]:
        result = await self._session.execute(
            select(ChatModel).where(ChatModel.id == chat_id)
        )
        return result.scalars().first()
