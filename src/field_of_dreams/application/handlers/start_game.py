from dataclasses import dataclass

from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.game import GameState
from field_of_dreams.domain.entities.player_turn import PlayerTurn
from ..common import Handler, UnitOfWork, ApplicationException
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway
from ..protocols.gateways.player_turn import PlayerTurnGateway
from ..protocols.gateways.user import UserGateway
from ..protocols.views.game import GameView


@dataclass(frozen=True)
class StartGameCommand:
    chat_id: ChatID


class StartGameHandler(Handler[StartGameCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        player_turn_gateway: PlayerTurnGateway,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        view: GameView,
        uow: UnitOfWork,
    ):
        self._game_gateway = game_gateway
        self._player_turn_gateway = player_turn_gateway
        self._player_gateway = player_gateway
        self._user_gateway = user_gateway
        self._view = view
        self._uow = uow

    async def execute(self, command: StartGameCommand) -> None:
        current_game = await self._game_gateway.get_current_game(
            command.chat_id
        )
        if current_game is None:
            raise ApplicationException("Игра не найдена.")

        queue = await self._player_gateway.get_players(
            current_game.id  # type: ignore
        )
        if len(queue) < 2:
            await self._game_gateway.delete_game(current_game)
            await self._uow.commit()
            raise ApplicationException(
                "Количество игроков довольно мало, чтобы начать игру."
            )

        player_turn = PlayerTurn(queue[0].id)  # type: ignore
        await self._player_turn_gateway.add_player_turn(player_turn)

        current_game.set_state(GameState.STARTED)
        first_user = await self._user_gateway.get_user_by_id(queue[0].user_id)
        await self._uow.commit()
        await self._view.notify_first_player_of_turn(
            current_game.chat_id, first_user
        )
