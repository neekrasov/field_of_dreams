from typing import Dict

from field_of_dreams.domain.entities.user import User, UserID
from field_of_dreams.application.protocols.user import UserGateway
from field_of_dreams.application.common import GatewayError


class InMemoryUserGateway(UserGateway):
    def __init__(self, users: Dict[UserID, User]):
        self._users = users

    async def add_user(self, user: User):
        if user.id not in self._users:
            user.id = max(self._users.keys(), default=0) + 1  # type: ignore
            self._users[user.id] = user
        else:
            raise GatewayError(f"User with id {user.id} already exists")
