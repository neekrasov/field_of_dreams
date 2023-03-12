from aiohttp.web import (
    Response,
    RouteTableDef,
    HTTPForbidden
)
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session, get_session

from field_of_dreams.core.common import Mediator, InvalidCredentials
from field_of_dreams.core.entities.admin import Admin
from field_of_dreams.core.handlers.admin_login import AdminLoginCommand
from field_of_dreams.core.handlers.get_admin_by_email import (
    GetAdminByEmailCommand,
)
from app.base import Request
from app.responses import json_response
from app.access import admin_required
from .schemes import AdminRequestSchema, AdminResponseSchema

router = RouteTableDef()


@docs(tags=['admin'])  # type: ignore
@request_schema(AdminRequestSchema())  # type: ignore
@response_schema(AdminResponseSchema())
@router.post("/admin.login")
async def admin_login(request: Request, mediator: Mediator) -> Response:
    data = request.get("data")
    try:
        admin: Admin = await mediator.send(
            AdminLoginCommand(
                data["email"],
                data["password"],
            )
        )
        session = await new_session(request)
        session["admin"] = {"email": admin.email, "id": admin.id}
    except InvalidCredentials:
        raise HTTPForbidden

    return json_response(AdminResponseSchema().dump(admin))


@docs(tags=['admin'])
@response_schema(AdminResponseSchema())  # type: ignore
@router.get("/admin.current")
@admin_required
async def get_current_admin(request: Request, mediator: Mediator) -> Response:
    session = await get_session(request)
    email = session.get("admin", {}).get("email")
    if email:
        try:
            admin: Admin = await mediator.send(GetAdminByEmailCommand(email))
            return json_response(AdminResponseSchema().dump(admin))
        except InvalidCredentials:
            raise HTTPForbidden
    raise HTTPForbidden
