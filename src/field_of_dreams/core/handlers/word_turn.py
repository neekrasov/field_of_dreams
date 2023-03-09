from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.user import UserID
from ..entities.player import PlayerState
from ..common import (
    Handler,
    UnitOfWork,
    ApplicationException,
    GameOver,
)
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway
from ..protocols.views.game import GameView
from ..services.score import generate_random_score


@dataclass(frozen=True)
class WordTurnCommand:
    chat_id: ChatID
    user_id: UserID
    word: str
    score_from: int
    score_to: int


class WordTurnHandler(Handler[WordTurnCommand, None]):
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

    async def execute(self, command: WordTurnCommand) -> None:
        async with self._uow.pipeline:
            user_id = command.user_id
            chat_id = command.chat_id
            word = command.word

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

            user_word = command.word.strip()
            word = current_game.word.word
            if word == user_word:
                score_per_turn = generate_random_score(
                    command.score_from, command.score_to
                )
                player.add_score(score_per_turn)
                current_game.finish()
                await self._game_view.notify_of_win_word(
                    chat_id,
                    word,
                    player.get_username(),
                    score_per_turn,
                    player.get_score(),
                )
            else:
                await self._game_view.notify_loss_word(
                    chat_id,
                    user_word,
                    player.get_username(),
                )
                player.is_active = False
                next_player = await self._player_gateway.get_next_player(
                    user_id, current_game.id  # type: ignore
                )
                if next_player:
                    next_player.state = PlayerState.PROCESSING
                    current_game.set_next_player(next_player)

            await self._game_gateway.update_game(current_game)
            await self._player_gateway.update_player(player)
            await self._uow.commit()

            if current_game.is_finished():
                raise GameOver(
                    (
                        "Игра завершилась! "
                        f"Победитель, {player.get_username()}! \n"
                        "Может ещё раз? /game"
                    )
                )
