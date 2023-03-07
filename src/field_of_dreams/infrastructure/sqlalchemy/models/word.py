from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    word: Mapped[str] = mapped_column()
    question: Mapped[str] = mapped_column()
