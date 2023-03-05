import random
from typing import Optional
from sqlalchemy.sql import func, select

from field_of_dreams.domain.entities.word import Word
from field_of_dreams.application.protocols.gateways.word import WordGateway
from .base import SqlalchemyGateway


class WordGatewayImpl(SqlalchemyGateway, WordGateway):
    async def add_word(self, word: Word) -> None:
        self._session.add(word)
        await self._try_flush()

    async def get_random_word(self) -> Optional[Word]:
        total_query = select(func.count()).select_from(Word)
        total_result = await self._session.execute(total_query)
        total = total_result.scalar()
        if not total:
            return None
        random_id = random.randint(1, total)
        word_query = select(Word).where(Word.id == random_id)  # type: ignore
        random_word = await self._session.execute(word_query)
        return random_word.scalar()
