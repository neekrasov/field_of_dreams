from aiohttp import web
from aiohttp_session import get_session
from aiohttp.web_exceptions import HTTPUnauthorized
from .types import Controller


def admin_required(handler: Controller):
    async def wrapped(request: web.Request):
        session = await get_session(request)
        if "admin" not in session:
            raise HTTPUnauthorized
        return await handler(request)

    return wrapped
