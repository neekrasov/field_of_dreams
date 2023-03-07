from typing import Protocol, Optional

from field_of_dreams.core.entities.word import Word


class WordGateway(Protocol):
    async def add_word(self, word: Word) -> None:
        raise NotImplementedError

    async def get_random_word(self) -> Optional[Word]:
        raise NotImplementedError
