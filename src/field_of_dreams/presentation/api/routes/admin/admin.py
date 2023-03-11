from aiohttp.web import Response, RouteTableDef
from aiohttp_apispec import request_schema, response_schema
from field_of_dreams.core.common import Mediator
from .schemes.admin import AdminSchema, UserSchema
from app.base import Request
from app.access import admin_required

router = RouteTableDef()


@request_schema(AdminSchema())
@response_schema(UserSchema())
@router.post("/admin.test")
@admin_required
async def test_controller(request: Request, mediator: Mediator) -> Response:
    print(request, mediator)
    return Response()
