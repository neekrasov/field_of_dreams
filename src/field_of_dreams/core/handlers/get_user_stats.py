from dataclasses import dataclass

from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.protocols.views import GameView
from field_of_dreams.core.protocols.gateways import UserStatsGateway
from ..common import Handler, UnitOfWork


@dataclass(slots=True)
class GetUserStatsCommand:
    user_id: UserID
    chat_id: ChatID
    username: str


class GetUserStatsHandler(Handler[GetUserStatsCommand, None]):
    def __init__(
        self,
        stats_gateway: UserStatsGateway,
        game_view: GameView,
        uow: UnitOfWork,
    ):
        self._stats_gateway = stats_gateway
        self._game_view = game_view
        self._uow = uow

    async def execute(self, command: GetUserStatsCommand) -> None:
        chat_id = command.chat_id
        username = command.username
        stats = await self._stats_gateway.get_user_stats(
            chat_id, command.user_id
        )
        if not stats:
            await self._game_view.notify_user_stats_not_found(
                command.chat_id, username
            )
            return

        await self._game_view.show_user_stats(chat_id, username, stats)
