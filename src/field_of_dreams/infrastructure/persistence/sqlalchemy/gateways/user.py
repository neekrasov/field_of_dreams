from sqlalchemy.sql import select

from field_of_dreams.domain.entities.user import User, UserID
from field_of_dreams.application.protocols.gateways.user import UserGateway
from .base import SqlalchemyGateway


class UserGatewayImpl(SqlalchemyGateway, UserGateway):
    async def add_user(self, user: User):
        self._session.add(user)
        await self._try_flush()

    async def get_user_by_id(self, user_id: UserID):
        result = await self._session.execute(
            select(User).where(User.id == user_id)  # type: ignore
        )
        return result.scalars().first()
