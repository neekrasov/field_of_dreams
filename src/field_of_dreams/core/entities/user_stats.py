from dataclasses import dataclass

from .chat import ChatID
from .user import UserID, User


@dataclass
class UserStats:
    chat_id: ChatID
    user_id: UserID
    total_score: int
    wins: int

    user: User
