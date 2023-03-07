from sqlalchemy.orm import mapped_column, Mapped

from field_of_dreams.core.entities.word import Word as WordEntity
from .base import Base


class Word(Base, WordEntity):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    word: Mapped[str] = mapped_column()
    question: Mapped[str] = mapped_column()
