import contextlib

from field_of_dreams.application.common import UnitOfWork
from typing import AsyncContextManager, AsyncGenerator


class FakeUnitOfWork(UnitOfWork):
    @contextlib.asynccontextmanager
    async def fake_transaction(self) -> AsyncGenerator:
        yield None

    @property
    def pipeline(  # type: ignore # noqa
        self,
    ) -> AsyncContextManager:
        return self.fake_transaction()

    async def commit(self) -> None:
        pass
