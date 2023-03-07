import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped

from field_of_dreams.domain.entities.player_turn import (
    TurnState,
)
from .base import Base


class PlayerTurn(Base):
    __tablename__ = "players_turns"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE")
    )
    state: Mapped[Enum] = mapped_column(
        Enum(TurnState), default=TurnState.IN_PROGRESS
    )
    start_time: Mapped[datetime] = mapped_column(default=datetime.utcnow())
