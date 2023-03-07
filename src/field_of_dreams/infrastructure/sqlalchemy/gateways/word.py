import random
from typing import Optional, cast
from dataclasses import asdict
from sqlalchemy.sql import func, select

from field_of_dreams.domain.entities.word import Word
from field_of_dreams.application.protocols.gateways.word import WordGateway
from .base import SqlalchemyGateway
from ..models import Word as WordModel


class WordGatewayImpl(SqlalchemyGateway, WordGateway):
    async def add_word(self, word: Word) -> None:
        self._session.add(WordModel(**asdict(word)))
        await self._try_flush()

    async def get_random_word(self) -> Optional[Word]:
        total_query = select(func.count()).select_from(WordModel)
        total_result = await self._session.execute(total_query)
        total = total_result.scalar()
        if not total:
            return None
        random_id = random.randint(1, total)
        word_query = select(WordModel).where(WordModel.id == random_id)
        random_word = await self._session.execute(word_query)
        return cast(Word, random_word.scalar())
