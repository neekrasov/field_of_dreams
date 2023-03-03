from typing import NewType
from dataclasses import dataclass

ChatID = NewType("ChatID", int)


@dataclass
class Chat:
    name: str
    id: ChatID
