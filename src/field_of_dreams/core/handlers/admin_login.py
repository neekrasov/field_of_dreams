from dataclasses import dataclass

from field_of_dreams.core.common import Handler, InvalidCredentials
from field_of_dreams.core.entities.admin import Admin
from ..services.hasher import PasswordHasher
from ..protocols.gateways.admin import AdminGateway


@dataclass(frozen=True)
class AdminLoginCommand:
    email: str
    raw_password: str


class AdminLoginHandler(Handler[AdminLoginCommand, Admin]):
    def __init__(
        self, hasher: PasswordHasher, admin_gateway: AdminGateway
    ) -> None:
        self._hasher = hasher
        self._admin_gateway = admin_gateway

    async def execute(self, command: AdminLoginCommand) -> Admin:
        admin = await self._admin_gateway.get_admin_by_email(command.email)

        if not admin:
            raise InvalidCredentials("Email not found: %s" % command.email)

        is_pass_valid = self._hasher.verify(
            command.raw_password, admin.hashed_password
        )

        if not is_pass_valid:
            raise InvalidCredentials("Password is not valid")

        return admin
