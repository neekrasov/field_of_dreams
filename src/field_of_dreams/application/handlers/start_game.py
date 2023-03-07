from dataclasses import dataclass

from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.game import GameState
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
        chat_id = command.chat_id
        current_game = await self._game_gateway.get_current_game(chat_id)
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
        turn_id = await self._player_turn_gateway.create_player_turn(
            queue[0].id  # type: ignore
        )
        word = current_game.word
        word_mask = word.get_mask(current_game.guessed_letters)
        current_game.set_state(GameState.STARTED)
        current_game.set_turn(turn_id)
        await self._uow.commit()

        await self._view.pin_word_mask(chat_id, word_mask, word.question)
        await self._view.show_queue(chat_id, queue)
