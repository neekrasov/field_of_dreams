from typing import Protocol

from field_of_dreams.domain.entities.user import User, UserID


class UserGateway(Protocol):
    async def add_user(self, user: User):
        raise NotImplementedError

    async def get_user_by_id(self, user_id: UserID):
        raise NotImplementedError
