from typing import Optional, NewType
from dataclasses import dataclass

WordID = NewType("WordID", int)


@dataclass
class Word:
    word: str
    question: str
    id: Optional[WordID] = None
