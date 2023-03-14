from typing import NewType, Optional
from dataclasses import dataclass


AdminID = NewType("AdminID", int)


@dataclass
class Admin:
    id: Optional[AdminID]
    email: str
    hashed_password: Optional[str] = None
