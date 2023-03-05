from field_of_dreams.domain.entities.user import User
from field_of_dreams.application.protocols.gateways.user import UserGateway
from .base import SqlalchemyGateway


class UserGatewayImpl(SqlalchemyGateway, UserGateway):
    async def add_user(self, user: User):
        self._session.add(user)
        await self._try_flush()
