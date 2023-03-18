import uuid
from datetime import datetime
from sqlalchemy import (
    Enum,
    ForeignKey,
    UniqueConstraint,
    BIGINT,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from field_of_dreams.core.entities.player import (
    PlayerState,
    Player as PlayerEntity,
)
from .base import Base
from .user import User


class Player(Base, PlayerEntity):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    game_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(), ForeignKey("users.id", ondelete="CASCADE")
    )
    state: Mapped[Enum] = mapped_column(
        Enum(PlayerState), default=PlayerState.WAITING
    )
    score: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    user: Mapped["User"] = relationship()
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", name="player_uc"),
    )
