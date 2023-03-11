from typing import Optional
from aiohttp.web import Application, Request as AiohttpRequest

from field_of_dreams.core.entities.admin import Admin


class Request(AiohttpRequest):
    admin: Optional[Admin] = None

    @property
    def app(self) -> Application:
        return super().app()  # type: ignore
