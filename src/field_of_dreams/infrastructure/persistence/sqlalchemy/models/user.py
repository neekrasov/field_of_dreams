from sqlalchemy import BIGINT
from sqlalchemy.orm import mapped_column, Mapped, registry

from field_of_dreams.domain.entities.user import User as UserEntity
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BIGINT(), primary_key=True, unique=True, index=True
    )
    name: Mapped[str] = mapped_column()


def map_user_table(mapper_registry: registry):
    mapper_registry.map_imperatively(UserEntity, User.__table__)
