import uuid
from datetime import datetime
from sqlalchemy import (
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column, Mapped, registry, relationship

from field_of_dreams.domain.entities.player import (
    PlayerState,
    Player as PlayerEntity,
)
from .base import Base, uuidpk
from .user import User


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuidpk]
    game_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    state: Mapped[Enum] = mapped_column(
        Enum(PlayerState), default=PlayerState.PLAYING
    )
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    user = relationship(User)

    __table_args__ = (UniqueConstraint("game_id", "user_id"),)


def map_player_table(mapper_registry: registry):
    mapper_registry.map_imperatively(PlayerEntity, Player.__table__)
