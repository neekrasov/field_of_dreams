from dataclasses import dataclass
from typing import Sequence

from field_of_dreams.core.common import (
    Handler,
    UnitOfWork,
    GatewayError,
    NotFoundError,
)
from field_of_dreams.core.entities.word import WordID, Word
from ..protocols.gateways.word import WordGateway


@dataclass(frozen=True)
class CreateWordCommand:
    word: str
    question: str


@dataclass(frozen=True)
class UpdateWordCommand:
    word_id: WordID
    word: str
    question: str


@dataclass(frozen=True)
class DeleteWordCommand:
    word_id: WordID


@dataclass(frozen=True)
class GetWordCommand:
    word: str


class CreateWordHandler(Handler[CreateWordCommand, None]):
    def __init__(
        self,
        word_gateway: WordGateway,
        uow: UnitOfWork,
    ) -> None:
        self._word_gateway = word_gateway
        self._uow = uow

    async def execute(self, command: CreateWordCommand) -> None:
        await self._word_gateway.create_word(
            command.word.lower(), command.question
        )
        await self._uow.commit()


class UpdateWordHandler(Handler[UpdateWordCommand, None]):
    def __init__(
        self,
        word_gateway: WordGateway,
        uow: UnitOfWork,
    ) -> None:
        self._word_gateway = word_gateway
        self._uow = uow

    async def execute(self, command: UpdateWordCommand) -> None:
        try:
            await self._word_gateway.update_word(
                command.word_id, command.word.lower(), command.question
            )
            await self._uow.commit()
        except GatewayError:
            raise NotFoundError("Word not found")


class DeleteWordHandler(Handler[DeleteWordCommand, None]):
    def __init__(
        self,
        word_gateway: WordGateway,
        uow: UnitOfWork,
    ) -> None:
        self._word_gateway = word_gateway
        self._uow = uow

    async def execute(self, command: DeleteWordCommand) -> None:
        try:
            await self._word_gateway.delete_word(command.word_id)
            await self._uow.commit()
        except GatewayError:
            raise NotFoundError("Word not found")


class GetWordHandler(Handler[GetWordCommand, Sequence[Word]]):
    def __init__(self, word_gateway: WordGateway) -> None:
        self._word_gateway = word_gateway

    async def execute(self, command: GetWordCommand) -> Sequence[Word]:
        words = await self._word_gateway.get_word(command.word.lower())

        if len(words) == 0:
            raise NotFoundError("Words not found")

        return words
