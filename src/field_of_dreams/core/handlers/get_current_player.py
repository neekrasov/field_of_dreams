from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.player import Player
from ..common import (
    Handler,
    UnitOfWork,
    ApplicationException,
)
from ..protocols.gateways.game import GameGateway


@dataclass(frozen=True)
class GetCurrentPlayerCommand:
    chat_id: ChatID


class GetCurrentPlayerHandler(Handler[GetCurrentPlayerCommand, Player]):
    def __init__(
        self,
        game_gateway: GameGateway,
        uow: UnitOfWork,
    ) -> None:
        self._game_gateway = game_gateway
        self._uow = uow

    async def execute(self, command: GetCurrentPlayerCommand) -> Player:
        async with self._uow.pipeline:
            chat_id = command.chat_id

            current_game = await self._game_gateway.get_current_game(chat_id)
            if not current_game:
                raise ApplicationException(
                    "Игра не создана. Начните игру командой /game."
                )
            player = current_game.cur_player
            if not player:
                raise ApplicationException(
                    "Не удалось обнаружить текущего игрока."
                )
            return player
