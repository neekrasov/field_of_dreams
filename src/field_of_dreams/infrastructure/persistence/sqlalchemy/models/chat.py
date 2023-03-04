from sqlalchemy.orm import mapped_column, Mapped, registry

from field_of_dreams.domain.entities.chat import Chat as ChatEntity
from .base import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column()


def map_chat_table(mapper_registry: registry):
    mapper_registry.map_imperatively(ChatEntity, Chat.__table__)
