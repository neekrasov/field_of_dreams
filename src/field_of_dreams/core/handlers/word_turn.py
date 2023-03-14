from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.game import Game
from ..entities.player import PlayerState
from ..common import (
    Handler,
    UnitOfWork,
    ApplicationException,
    GameOver,
)
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway
from ..protocols.gateways.user_stats import UserStatsGateway
from ..protocols.views.game import GameView
from ..services.score import generate_random_score


@dataclass(frozen=True)
class WordTurnCommand:
    chat_id: ChatID
    word: str


class WordTurnHandler(Handler[WordTurnCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        player_gateway: PlayerGateway,
        game_view: GameView,
        stats_gateway: UserStatsGateway,
        uow: UnitOfWork,
        score_from: int,
        score_to: int,
    ) -> None:
        self._game_gateway = game_gateway
        self._player_gateway = player_gateway
        self._game_view = game_view
        self._stats_gateway = stats_gateway
        self._uow = uow
        self._score_from = score_from
        self._score_to = score_to

    async def execute(self, command: WordTurnCommand) -> None:
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

            user_word = command.word.strip().lower()
            word = current_game.word.word.strip().lower()

            if word == user_word:
                score_per_turn = generate_random_score(
                    self._score_from, self._score_to
                )
                player.add_score(score_per_turn)
                current_game.finish()

                stats = await self._stats_gateway.get_user_stats(
                    chat_id, player.user_id
                )
                stats.total_score += player.score
                stats.wins += 1
                await self._stats_gateway.update_stats(stats)

                await self._game_view.notify_of_win_word(
                    chat_id,
                    word,
                    player.username,
                    score_per_turn,
                    player.score,
                )
            else:
                if user_word.isnumeric():
                    await self._game_view.notify_dont_support_numeric(
                        chat_id, player.username
                    )
                elif current_game.word.contain_punctuation:
                    await self._game_view.notify_dont_support_punctuation(
                        chat_id, player.username
                    )
                else:
                    await self._game_view.notify_loss_word(
                        chat_id,
                        user_word,
                        player.username,
                    )
                player.is_active = False
                await self._player_gateway.update_player(player)
                next_player = await self._player_gateway.get_next_player(
                    player, current_game.id  # type: ignore
                )
                if next_player:
                    next_player.state = PlayerState.PROCESSING
                    current_game.set_next_player(next_player)
                    await self._player_gateway.update_player(next_player)
                else:
                    current_game.finish()
                    await self._finish(current_game, chat_id)
                    raise GameOver(
                        "🫤 Игра завершилась ничьёй,"
                        "никто не угадал слово... \n"
                        "Попробуйте ещё раз! /game"
                    )

            if current_game.is_finished():
                await self._finish(current_game, chat_id)
                raise GameOver(
                    (
                        "🥳 Игра завершилась! "
                        f"Победитель, {player.username}! \n"
                        "Может ещё раз? /game"
                    )
                )
            else:
                await self._game_gateway.update_game(current_game)

    async def _finish(self, game: Game, chat_id: ChatID):
        await self._game_view.unpin_word_mask(chat_id)
        await self._game_gateway.update_game(game)
        await self._uow.commit()
