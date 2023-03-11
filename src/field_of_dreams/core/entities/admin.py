from typing import NewType
from dataclasses import dataclass

AdminID = NewType("AdminID", int)


@dataclass
class Admin:
    id: AdminID
    email: str
    hashed_password: str
