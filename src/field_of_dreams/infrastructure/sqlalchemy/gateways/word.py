from typing import Optional, Sequence
from sqlalchemy.sql import func, select

from field_of_dreams.core.common import GatewayError
from field_of_dreams.core.entities.word import Word, WordID
from field_of_dreams.core.protocols.gateways.word import WordGateway
from .base import SqlalchemyGateway
from ..models import Word as WordModel


class WordGatewayImpl(SqlalchemyGateway, WordGateway):
    async def create_word(self, word: str, question: str) -> None:
        db_word = WordModel(word=word, question=question)
        self._session.add(db_word)

    async def get_random_word(self) -> Optional[Word]:
        stmt = select(WordModel).order_by(func.random()).limit(1)
        random_word = await self._session.execute(stmt)
        return random_word.scalars().first()

    async def get_word(self, word: str) -> Sequence[Word]:
        word_result = await self._session.execute(
            select(WordModel).where(WordModel.word == word)
        )
        return word_result.scalars().all()

    # TODO Можно ли сразу удалить без лишнего запроса?
    async def delete_word(self, word_id: WordID) -> None:
        word_db = await self.get_if_exists(word_id)
        await self._session.delete(word_db)
        await self._try_flush()

    async def update_word(
        self, word_id: WordID, word: str, question: str
    ) -> None:
        word_db = await self.get_if_exists(word_id)
        word_db.question = question
        word_db.word = word
        await self._try_flush()

    async def get_if_exists(self, word_id: WordID) -> Word:
        word_result = await self._session.execute(
            select(WordModel).where(WordModel.id == word_id)
        )
        word = word_result.scalars().first()

        if not word:
            raise GatewayError("Word not found")
        return word
