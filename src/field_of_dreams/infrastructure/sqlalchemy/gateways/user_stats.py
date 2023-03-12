from typing import Sequence
from sqlalchemy.sql import select, and_, or_, update, desc
from sqlalchemy.orm import joinedload

from field_of_dreams.core.entities.user_stats import UserStats
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.protocols.gateways.user_stats import UserStatsGateway
from .base import SqlalchemyGateway
from ..models import UserStats as UserStatsModel


class UserStatsGatewayImpl(SqlalchemyGateway, UserStatsGateway):
    async def get_user_stats(
        self, chat_id: ChatID, user_id: UserID
    ) -> UserStats:
        stats_result = await self._session.execute(
            select(UserStatsModel).where(
                and_(
                    UserStatsModel.user_id == user_id,
                    UserStatsModel.chat_id == chat_id,
                )
            )
        )
        return stats_result.scalars().first()

    async def get_chat_stats(
        self, chat_id: ChatID, top: int = 10
    ) -> Sequence[UserStats]:
        stats_result = await self._session.execute(
            select(UserStatsModel)
            .options(joinedload(UserStatsModel.user))
            .where(
                and_(
                    UserStatsModel.chat_id == chat_id,
                    or_(
                        UserStatsModel.wins != 0,
                        UserStatsModel.total_score != 0,
                    ),
                )
            )
            .order_by(desc(UserStatsModel.wins))
            .limit(top)
        )
        return stats_result.scalars().all()

    async def create_user_stats(
        self, chat_id: ChatID, user_id: UserID
    ) -> None:
        stats_db = UserStatsModel(
            user_id=user_id,
            chat_id=chat_id,
        )
        self._session.add(stats_db)
        await self._try_flush()

    async def update_stats(self, stats: UserStats) -> None:
        await self._session.execute(
            update(UserStatsModel)
            .where(
                UserStatsModel.chat_id == stats.chat_id,
                UserStatsModel.user_id == stats.user_id,
            )
            .values(
                user_id=stats.user_id,
                chat_id=stats.chat_id,
                total_score=stats.total_score,
                wins=stats.wins,
            )
        )
        await self._try_flush()
