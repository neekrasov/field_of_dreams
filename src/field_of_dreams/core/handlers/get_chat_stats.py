from dataclasses import dataclass

from ..entities.chat import ChatID
from ..common import Handler, UnitOfWork
from ..protocols.views.game import GameView
from ..protocols.gateways.user_stats import UserStatsGateway
from ..protocols.gateways.chat import ChatGateway


@dataclass(frozen=True)
class GetChatStatsCommand:
    chat_id: ChatID


class GetChatStatsHandler(Handler[GetChatStatsCommand, None]):
    def __init__(
        self,
        chat_gateway: ChatGateway,
        stats_gateway: UserStatsGateway,
        game_view: GameView,
        uow: UnitOfWork,
    ) -> None:
        self._stats_gateway = stats_gateway
        self._chat_gateway = chat_gateway
        self._game_view = game_view
        self._uow = uow

    async def execute(self, command: GetChatStatsCommand) -> None:
        async with self._uow.pipeline:
            chat_id = command.chat_id
            chat = await self._chat_gateway.get_chat_by_id(chat_id)
            if not chat:
                await self._game_view.notify_empty_stats_chat_not_exists(
                    chat_id
                )
                return

            stats = await self._stats_gateway.get_chat_stats(chat_id)
            if len(stats) == 0:
                await self._game_view.notify_empty_stats(chat_id)
                return

            await self._game_view.show_stats(chat_id, stats)
