from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.user import UserID
from ..common import (
    Handler,
    UnitOfWork,
    QueueAccessError,
    ApplicationException,
)
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway
from ..protocols.views.game import GameView


@dataclass(frozen=True)
class CheckUserQueueCommand:
    chat_id: ChatID
    user_id: UserID


class CheckUserQueueHandler(Handler[CheckUserQueueCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        player_gateway: PlayerGateway,
        game_view: GameView,
        uow: UnitOfWork,
    ) -> None:
        self._game_gateway = game_gateway
        self._player_gateway = player_gateway
        self._game_view = game_view
        self._uow = uow

    async def execute(self, command: CheckUserQueueCommand) -> None:
        user_id = command.user_id
        chat_id = command.chat_id

        current_game = await self._game_gateway.get_current_game(chat_id)
        if not current_game:
            raise ApplicationException(
                "Игра не создана. Начните игру командой /game."
            )
        check_user = current_game.check_user_queue(user_id)
        if not check_user:
            raise QueueAccessError(
                f"Очередь пользователя {current_game.cur_player.get_username()}"  # type: ignore # noqa
            )
