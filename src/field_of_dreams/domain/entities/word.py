from typing import Optional, NewType, List
from dataclasses import dataclass

WordID = NewType("WordID", int)


@dataclass
class Word:
    word: str
    question: str
    id: Optional[WordID] = None

    def get_mask(self, shown_letters: List[str]) -> str:
        shown_letters_set = set(shown_letters)
        return "".join(c if c in shown_letters_set else "_" for c in self.word)
