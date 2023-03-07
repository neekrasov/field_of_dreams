from sqlalchemy.sql import select

from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.protocols.gateways.user import UserGateway
from .base import SqlalchemyGateway
from ..models import User as UserModel


class UserGatewayImpl(SqlalchemyGateway, UserGateway):
    async def create_user(self, user_id: UserID, username: str):
        db_user = UserModel(id=user_id, name=username)
        self._session.add(db_user)
        await self._try_flush()

    async def get_user_by_id(self, user_id: UserID):
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)  # type: ignore
        )
        return result.scalars().first()
