from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from field_of_dreams.application.common.exception import GatewayError


class SqlalchemyGateway:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _try_flush(
        self,
    ):
        try:
            await self._session.flush()
        except IntegrityError as e:
            raise GatewayError(str(e))
