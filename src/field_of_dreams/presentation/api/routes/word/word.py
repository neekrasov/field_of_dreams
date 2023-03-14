import logging
from typing import Sequence
from aiohttp.web import Response, RouteTableDef
from aiohttp_apispec import (
    request_schema,
    response_schema,
    docs,
    querystring_schema,
)

from app.base import Request
from app.responses import json_response
from app.access import admin_required
from field_of_dreams.core.common import Mediator
from field_of_dreams.core.entities.word import Word
from field_of_dreams.core.handlers.crud_word import (
    CreateWordCommand,
    UpdateWordCommand,
    DeleteWordCommand,
    GetWordCommand,
)
from .schemes import (
    WordResponseSchema,
    GetWordRequestSchema,
    GetWordResponseSchema,
    CreateWordRequestSchema,
    UpdateWordRequestSchema,
    DeleteWordRequestSchema,
)

router = RouteTableDef()
logger = logging.getLogger()


@docs(tags=["word"])
@querystring_schema(GetWordRequestSchema())  # type: ignore
@response_schema(GetWordResponseSchema())
@router.get("/word")
@admin_required
async def get_word(request: Request, mediator: Mediator) -> Response:
    word = request.query.get("word")
    logger.info("Get word %s", word)
    words: Sequence[Word] = await mediator.send(
        GetWordCommand(request.query.get("word"))
    )
    return json_response(
        GetWordResponseSchema().dump(
            {"words": [WordResponseSchema().dump(word) for word in words]}
        )
    )


@docs(tags=["word"])
@request_schema(CreateWordRequestSchema())  # type: ignore
@router.post("/word")
@admin_required
async def create_word(request: Request, mediator: Mediator) -> Response:
    data = request.get("data")
    logger.info(
        "Create word %s with question %s", data["word"], data["question"]
    )
    await mediator.send(CreateWordCommand(data["word"], data["question"]))
    return Response(status=200)


@docs(tags=["word"])
@request_schema(UpdateWordRequestSchema())  # type: ignore
@router.patch("/word")
@admin_required
async def update_word(request: Request, mediator: Mediator) -> Response:
    data = request.get("data")
    logger.info("Update word %s with id %s", data["word"], data["id"])
    await mediator.send(
        UpdateWordCommand(data["id"], data["word"], data["question"])
    )
    return Response(status=200)


@docs(tags=["word"])
@request_schema(DeleteWordRequestSchema())  # type: ignore
@router.delete("/word")
@admin_required
async def delete_word(request: Request, mediator: Mediator) -> Response:
    data = request.get("data")
    logger.info("Delete word with id %s", data["id"])
    await mediator.send(DeleteWordCommand(data["id"]))
    return Response(status=200)
