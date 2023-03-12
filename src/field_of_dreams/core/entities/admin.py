from typing import NewType, Optional
from dataclasses import dataclass


AdminID = NewType("AdminID", int)


@dataclass
class Admin:
    email: str
    id: Optional[AdminID] = None
    hashed_password: Optional[str] = None
