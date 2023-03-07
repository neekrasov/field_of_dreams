from sqlalchemy import BIGINT
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BIGINT(), primary_key=True, unique=True, index=True
    )
    name: Mapped[str] = mapped_column()
