from typing import NewType
from dataclasses import dataclass


UserID = NewType("UserID", int)


@dataclass
class User:
    id: UserID
    name: str
