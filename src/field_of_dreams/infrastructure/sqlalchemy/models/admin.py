from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
