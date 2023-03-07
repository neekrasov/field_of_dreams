from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    title: Mapped[str] = mapped_column()
