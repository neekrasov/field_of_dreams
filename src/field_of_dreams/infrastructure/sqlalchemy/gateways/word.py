from typing import Optional
from dataclasses import asdict
from sqlalchemy.sql import func, select

from field_of_dreams.core.entities.word import Word
from field_of_dreams.core.protocols.gateways.word import WordGateway
from .base import SqlalchemyGateway
from ..models import Word as WordModel


class WordGatewayImpl(SqlalchemyGateway, WordGateway):
    async def add_word(self, word: Word) -> None:
        self._session.add(WordModel(**asdict(word)))
        await self._try_flush()

    async def get_random_word(self) -> Optional[Word]:
        stmt = select(WordModel).order_by(func.random()).limit(1)
        random_word = await self._session.execute(stmt)
        return random_word.scalars().first()
