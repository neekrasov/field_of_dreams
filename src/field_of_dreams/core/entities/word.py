import string
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

    def check_guess(self, letter: str) -> bool:
        if letter.lower() in self.word.lower():
            return True
        return False

    def count_letter(self, letter: str) -> int:
        return self.word.count(letter)

    def is_last_letter(self, shown_letters: List[str]):
        remaining_chars = set(self.word) - set(shown_letters)
        return len(remaining_chars) == 1

    @property
    def contain_punctuation(self):
        return any(char in string.punctuation for char in self.word)
