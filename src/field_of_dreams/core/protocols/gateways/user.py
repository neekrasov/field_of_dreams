from typing import Protocol

from field_of_dreams.core.entities.user import UserID


class UserGateway(Protocol):
    async def create_user(self, user_id: UserID, username: str):
        raise NotImplementedError

    async def get_user_by_id(self, user_id: UserID):
        raise NotImplementedError
