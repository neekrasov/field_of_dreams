from typing import Optional
from sqlalchemy.sql import select

from field_of_dreams.core.entities.admin import Admin
from field_of_dreams.core.protocols.gateways.admin import AdminGateway
from .base import SqlalchemyGateway
from ..models.admin import Admin as AdminModel


class AdminGatewayImpl(SqlalchemyGateway, AdminGateway):
    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        admin_result = await self._session.execute(
            select(AdminModel).where(AdminModel.email == email)  # type: ignore
        )
        return admin_result.scalars().first()

    async def create_admin(self, email: str, hashed_password: str) -> None:
        db_admin = AdminModel(email=email, hashed_password=hashed_password)  # type: ignore # noqa
        self._session.add(db_admin)
        await self._try_flush()
