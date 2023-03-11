from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from field_of_dreams.core.entities.user_stats import UserStats
from .base import Base
from .user import User


class UserStats(Base, UserStats):
    __tablename__ = "user_stats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    total_score: Mapped[int] = mapped_column(default=0)
    wins: Mapped[int] = mapped_column(default=0)

    user: Mapped[User] = relationship()

    __table_args__ = (PrimaryKeyConstraint("user_id", "chat_id"),)
