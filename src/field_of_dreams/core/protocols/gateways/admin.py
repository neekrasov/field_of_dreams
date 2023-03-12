from typing import Protocol, Optional

from field_of_dreams.core.entities.admin import Admin


class AdminGateway(Protocol):
    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        raise NotImplementedError

    async def create_admin(self, email: str, hashed_password: str) -> None:
        raise NotImplementedError
