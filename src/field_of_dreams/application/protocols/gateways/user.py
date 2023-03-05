from typing import Protocol

from field_of_dreams.domain.entities.user import User


class UserGateway(Protocol):
    async def add_user(self, user: User):
        raise NotImplementedError
