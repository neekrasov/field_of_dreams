from typing import Protocol, Optional, Sequence

from field_of_dreams.core.entities.word import Word, WordID


class WordGateway(Protocol):
    async def create_word(self, word: str, question: str) -> None:
        raise NotImplementedError

    async def get_random_word(self) -> Optional[Word]:
        raise NotImplementedError

    async def get_word(self, word: str) -> Sequence[Word]:
        raise NotImplementedError

    async def delete_word(self, word_id: WordID) -> None:
        raise NotImplementedError

    async def update_word(self, word_id: WordID, word: str, question: str):
        raise NotImplementedError
