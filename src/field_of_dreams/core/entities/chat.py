from typing import NewType
from dataclasses import dataclass

ChatID = NewType("ChatID", int)


@dataclass
class Chat:
    title: str
    id: ChatID
