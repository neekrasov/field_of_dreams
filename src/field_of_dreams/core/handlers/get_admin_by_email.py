from dataclasses import dataclass

from field_of_dreams.core.common import Handler, InvalidCredentials
from field_of_dreams.core.entities.admin import Admin
from ..protocols.gateways.admin import AdminGateway


@dataclass
class GetAdminByEmailCommand:
    email: str


class GetAdminByEmailHandler(Handler[GetAdminByEmailCommand, Admin]):
    def __init__(
        self, admin_gateway: AdminGateway
    ) -> None:
        self._admin_gateway = admin_gateway

    async def execute(self, command: GetAdminByEmailCommand) -> Admin:
        admin = await self._admin_gateway.get_admin_by_email(command.email)

        if not admin:
            raise InvalidCredentials("Email not found: %s" % command.email)

        return admin
