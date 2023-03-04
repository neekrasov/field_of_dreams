from sqlalchemy.orm import mapped_column, Mapped, registry

from field_of_dreams.domain.entities.word import Word as WordEntity
from .base import Base


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    word: Mapped[str] = mapped_column()
    question: Mapped[str] = mapped_column()


def map_word_table(mapper_registry: registry):
    mapper_registry.map_imperatively(WordEntity, Word.__table__)
