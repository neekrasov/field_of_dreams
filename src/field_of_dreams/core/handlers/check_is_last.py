from dataclasses import dataclass

from ..entities.chat import ChatID
from ..common import Handler, UnitOfWork
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway


@dataclass(frozen=True)
class CheckLastPlayerCommand:
    chat_id: ChatID


class CheckLastPlayerHandler(Handler[CheckLastPlayerCommand, bool]):
    def __init__(
        self,
        game_gateway: GameGateway,
        player_gateway: PlayerGateway,
        uow: UnitOfWork,
    ) -> None:
        self._game_gateway = game_gateway
        self._player_gateway = player_gateway
        self._uow = uow

    async def execute(self, command: CheckLastPlayerCommand) -> bool:
        chat_id = command.chat_id
        current_game = await self._game_gateway.get_current_game(chat_id)  # type: ignore # noqa
        players = await self._player_gateway.get_players(current_game.id)  # type: ignore # noqa
        return len(players) == 1
