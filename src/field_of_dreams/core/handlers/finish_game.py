from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.user import UserID
from ..common import (
    Handler,
    UnitOfWork,
    ApplicationException,
)
from ..protocols.gateways.game import GameGateway
from ..protocols.views.game import GameView


@dataclass(frozen=True)
class FinishGameCommand:
    chat_id: ChatID
    user_id: UserID
    is_admin: bool


class FinishGameHandler(Handler[FinishGameCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        game_view: GameView,
        uow: UnitOfWork,
    ) -> None:
        self._game_gateway = game_gateway
        self._game_view = game_view
        self._uow = uow

    async def execute(self, command: FinishGameCommand) -> None:
        async with self._uow.pipeline:
            chat_id = command.chat_id
            current_game = await self._game_gateway.get_current_game(chat_id)
            if not current_game:
                raise ApplicationException(
                    "Игра не создана. Начните игру командой /game."
                )
            if (
                current_game.author_id != command.user_id
                and not command.is_admin
            ):
                raise ApplicationException(
                    (
                        "Игру может остановить только "
                        "администратор чата, или инициатор игры"
                    )
                )
            current_game.finish()
            await self._uow.commit()

            await self._game_view.unpin_word_mask(chat_id)
