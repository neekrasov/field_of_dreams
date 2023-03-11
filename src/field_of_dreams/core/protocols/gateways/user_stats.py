from typing import Protocol, Sequence

from field_of_dreams.core.entities.user_stats import UserStats
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID


class UserStatsGateway(Protocol):
    async def get_user_stats(
        self, chat_id: ChatID, user_id: UserID
    ) -> UserStats:
        raise NotImplementedError

    async def get_chat_stats(
        self, chat_id: ChatID, top: int = 10
    ) -> Sequence[UserStats]:
        raise NotImplementedError

    async def create_user_stats(
        self, chat_id: ChatID, user_id: UserID
    ) -> None:
        raise NotImplementedError

    async def update_stats(self, stats: UserStats) -> None:
        raise NotImplementedError
