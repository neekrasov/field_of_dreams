import random
from typing import Dict

from field_of_dreams.domain.entities.word import Word, WordID
from field_of_dreams.application.protocols.word import WordGateway


class InMemoryWordGateway(WordGateway):
    def __init__(self, words: Dict[WordID, Word]):
        self._words = words

    async def add_word(self, word: Word):
        self.words[word.id] = word  # type: ignore

    async def get_random_word(self) -> Word:
        return random.choice(list(self._words.values()))
