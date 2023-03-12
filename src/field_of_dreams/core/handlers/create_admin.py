from dataclasses import dataclass

from field_of_dreams.core.common import (
    Handler,
    GatewayError,
    ApplicationException,
    UnitOfWork,
)
from ..services.hasher import PasswordHasher
from ..protocols.gateways.admin import AdminGateway


@dataclass(frozen=True)
class CreateAdminCommand:
    email: str
    raw_password: str


class CreateAdminHandler(Handler[CreateAdminCommand, None]):
    def __init__(
        self,
        hasher: PasswordHasher,
        admin_gateway: AdminGateway,
        uow: UnitOfWork,
    ) -> None:
        self._admin_gateway = admin_gateway
        self._hasher = hasher
        self._uow = uow

    async def execute(self, command: CreateAdminCommand) -> None:
        hashed_password = self._hasher.hash(command.raw_password)
        try:
            await self._admin_gateway.create_admin(
                command.email, hashed_password
            )
            await self._uow.commit()
        except GatewayError:
            raise ApplicationException("Admin already exists")
