import uuid
from datetime import datetime
from sqlalchemy import (
    Enum,
    ForeignKey,
    UniqueConstraint,
    BIGINT,
)
from sqlalchemy.orm import mapped_column, Mapped, registry

from field_of_dreams.domain.entities.player import (
    PlayerState,
    Player as PlayerEntity,
)
from .base import Base, uuidpk


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuidpk]
    game_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(), ForeignKey("users.id", ondelete="CASCADE")
    )
    state: Mapped[Enum] = mapped_column(
        Enum(PlayerState), default=PlayerState.PLAYING
    )
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    __table_args__ = (UniqueConstraint("game_id", "user_id"),)


def map_player_table(mapper_registry: registry):
    mapper_registry.map_imperatively(PlayerEntity, Player.__table__)
