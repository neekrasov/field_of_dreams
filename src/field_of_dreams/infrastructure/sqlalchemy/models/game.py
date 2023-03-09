from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import (
    Enum,
    ARRAY,
    CHAR,
    ForeignKey,
    BIGINT,
    Interval,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from field_of_dreams.core.entities.game import (
    Game as GameEntity,
    GameState,
)
from .base import Base, uuidpk
from .word import Word

if TYPE_CHECKING:
    from .player import Player


class Game(Base, GameEntity):
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
    cur_player_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE", use_alter=True),
    )
    state: Mapped[Enum] = mapped_column(
        Enum(GameState), default=GameState.CREATED
    )
    interval: Mapped[timedelta] = mapped_column(Interval())
    guessed_letters: Mapped[List[str]] = mapped_column(ARRAY(CHAR), default=[])
    start_time: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    end_time: Mapped[Optional[datetime]] = mapped_column()

    word: Mapped[Word] = relationship()
    cur_player: Mapped[Optional["Player"]] = relationship(
        foreign_keys=cur_player_id
    )
