from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Enum,
    ARRAY,
    CHAR,
    ForeignKey,
    BIGINT,
)
from sqlalchemy.orm import mapped_column, Mapped, registry

from field_of_dreams.domain.entities.game import (
    Game as GameEntity,
    GameState,
)
from .base import Base, uuidpk


class Game(Base):
    __tablename__ = "games"

    id: Mapped[uuidpk]
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE")
    )
    author_id: Mapped[int] = mapped_column(
        BIGINT(), ForeignKey("users.id", ondelete="CASCADE")
    )
    current_turn_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players_turns.id", ondelete="CASCADE", use_alter=True)
    )
    state: Mapped[Enum] = mapped_column(
        Enum(GameState), default=GameState.PREPARING
    )
    guessed_letters: Mapped[ARRAY] = mapped_column(ARRAY(CHAR), default=[])
    failed_letters: Mapped[ARRAY] = mapped_column(ARRAY(CHAR), default=[])
    start_time: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    end_time: Mapped[Optional[datetime]] = mapped_column()


def map_game_table(mapper_registry: registry):
    mapper_registry.map_imperatively(GameEntity, Game.__table__)
