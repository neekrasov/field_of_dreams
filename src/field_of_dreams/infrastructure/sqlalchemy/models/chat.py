from sqlalchemy import BIGINT
from sqlalchemy.orm import mapped_column, Mapped

from field_of_dreams.core.entities.chat import Chat as ChatEntity
from .base import Base


class Chat(Base, ChatEntity):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        BIGINT(), primary_key=True, unique=True, index=True
    )
    title: Mapped[str] = mapped_column()
