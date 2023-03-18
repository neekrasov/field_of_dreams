import json
import aiohttp_session
from typing import Awaitable
from aiohttp_apispec import validation_middleware
from aiohttp.web_response import StreamResponse
from aiohttp.web_middlewares import middleware
from aiohttp.web_exceptions import HTTPClientError, HTTPUnprocessableEntity
from aiohttp.web import Application, Request, HTTPUnauthorized
from di import ScopeState

from field_of_dreams.core.entities.admin import Admin
from field_of_dreams.core.common import InvalidCredentials, NotFoundError
from field_of_dreams.infrastructure.di import DIContainer, DIScope
from .types import Controller
from .responses import error_json_response

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: Request, handler: Controller):
    try:
        response = await handler(request)
        return response
    except NotFoundError as e:
        return error_json_response(
            http_status=404,
            status=HTTP_ERROR_CODES[404],
            message=e.message,
        )
    except InvalidCredentials as e:
        return error_json_response(
            http_status=403,
            status=HTTP_ERROR_CODES[403],
            message=e.message,
        )
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),  # type: ignore
        )
    except HTTPClientError as e:
        return error_json_response(
            http_status=e.status_code,
            status=HTTP_ERROR_CODES[e.status_code],
            message=e.reason,
        )


@middleware
async def auth_middleware(request: Request, handler: Controller):
    session = await aiohttp_session.get_session(request)
    if session:
        request.admin = Admin(
            id=session["admin"]["id"], email=session["admin"]["email"]
        )
    return await handler(request)


@middleware
async def admin_auth(request: Request, handler: Controller):
    # check if admin before di middleware
    # but handler has extra args for resolving
    if hasattr(handler.keywords["handler"], "admin_required"):  # type: ignore
        session = await aiohttp_session.get_session(request)
        if "admin" not in session:
            raise HTTPUnauthorized
    return await handler(request)


def create_di_middleware(
    container: DIContainer,
    app_state: ScopeState,
):
    @middleware
    async def e(
        request: Request, handler: Controller
    ) -> Awaitable[StreamResponse]:
        async with container.enter_scope(
            DIScope.REQUEST, app_state
        ) as request_state:
            return await container.execute(
                handler=handler,
                state=request_state,
                scope=DIScope.REQUEST,
                values={Request: request},
            )

    return e


def setup_middlewares(
    app: Application,
    container: DIContainer,
    app_state: ScopeState,
):
    app.middlewares.append(validation_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(
        aiohttp_session.session_middleware(
            aiohttp_session.SimpleCookieStorage()
        )
    )
    app.middlewares.append(admin_auth)
    app.middlewares.append(create_di_middleware(container, app_state))
