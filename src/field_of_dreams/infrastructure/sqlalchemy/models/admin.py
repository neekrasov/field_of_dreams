from sqlalchemy.orm import mapped_column, Mapped

from field_of_dreams.core.entities.admin import Admin
from .base import Base


class Admin(Base, Admin):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
