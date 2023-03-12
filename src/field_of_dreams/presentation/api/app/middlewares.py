import json
import aiohttp_session
from typing import Optional, Awaitable
from aiohttp_apispec import validation_middleware
from aiohttp.web_response import StreamResponse
from aiohttp.web_middlewares import middleware
from aiohttp.web_exceptions import HTTPClientError, HTTPUnprocessableEntity
from aiohttp.web import Application, Request, json_response
from di import Container, ScopeState
from di.executors import AsyncExecutor
from di.dependent import Dependent

from field_of_dreams.core.entities.admin import Admin
from field_of_dreams.infrastructure.di.container import DIScope
from .types import Controller

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
        admin = Admin(email=session["admin"]["email"])
        request.admin = admin
    return await handler(request)


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return json_response(
        status=http_status,
        data={"status": status, "message": str(message), "data": data},
    )


def create_di_middleware(container: Container, app_state: ScopeState):
    @middleware
    async def e(
        request: Request, handler: Controller
    ) -> Awaitable[StreamResponse]:
        solved = container.solve(
            Dependent(handler, scope=DIScope.REQUEST),
            scopes=[DIScope.APP, DIScope.REQUEST],
        )
        async with container.enter_scope(
            DIScope.REQUEST, app_state
        ) as request_state:
            return await solved.execute_async(
                executor=AsyncExecutor(),
                state=request_state,
                values={
                    Request: request,
                },
            )

    return e


def setup_middlewares(
    app: Application, container: Container, app_state: ScopeState
):
    app.middlewares.append(validation_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(
        aiohttp_session.session_middleware(
            aiohttp_session.SimpleCookieStorage()
        )
    )
    app.middlewares.append(create_di_middleware(container, app_state))
