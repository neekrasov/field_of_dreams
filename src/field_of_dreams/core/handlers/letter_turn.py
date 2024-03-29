import string
from dataclasses import dataclass

from ..entities.chat import ChatID
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
from ..services.score import make_score


@dataclass(frozen=True)
class LetterTurnCommand:
    chat_id: ChatID
    letter: str


class LetterTurnHandler(Handler[LetterTurnCommand, None]):
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

    async def execute(self, command: LetterTurnCommand) -> None:
        async with self._uow.pipeline:
            chat_id = command.chat_id
            letter = command.letter

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

            word = current_game.word
            guessed_right = False
            if letter in string.punctuation:
                await self._game_view.notify_dont_support_punctuation(
                    chat_id, player.username
                )
            elif letter.isnumeric():
                await self._game_view.notify_dont_support_numeric(
                    chat_id, player.username
                )
            elif current_game.check_already_guessed_letter(letter):
                await self._game_view.already_guessed_letter(
                    chat_id, letter, player.username
                )
            elif word.check_guess(letter):
                guessed_right = True
                is_last = word.is_last_letter(current_game.guessed_letters)
                score_per_turn = make_score(self._score_from, self._score_to)
                showed_pos_count = word.count_letter(letter)
                result_score_turn = score_per_turn * showed_pos_count
                player.add_score(result_score_turn)
                current_game.add_guessed_letter(letter)
                if is_last:
                    stats = await self._stats_gateway.get_user_stats(
                        chat_id, player.user_id
                    )
                    stats.total_score += player.score
                    stats.wins += 1
                    await self._stats_gateway.update_stats(stats)

                    current_game.finish()
                    await self._game_view.update_word_mask(
                        chat_id,
                        word.get_mask(current_game.guessed_letters),
                        word.question,
                    )
                    await self._game_view.notify_winner_letter(
                        chat_id,
                        letter,
                        player.username,
                        showed_pos_count,
                        result_score_turn,
                        player.score,
                    )
                else:
                    await self._game_view.notify_correct_letter(
                        chat_id,
                        letter,
                        showed_pos_count,
                        player.username,
                        result_score_turn,
                    )
                    await self._game_view.update_word_mask(
                        chat_id,
                        word.get_mask(current_game.guessed_letters),
                        word.question,
                    )
            else:
                await self._game_view.notify_wrong_letter(
                    chat_id, letter, player.username
                )

            player.state = PlayerState.WAITING
            if not current_game.is_finished() and not guessed_right:
                next_player = await self._player_gateway.get_next_player(
                    player, current_game.id  # type: ignore
                )
                if next_player:
                    next_player.state = PlayerState.PROCESSING
                    current_game.set_next_player(next_player)
                    await self._player_gateway.update_player(next_player)

            await self._game_gateway.update_game(current_game)
            await self._player_gateway.update_player(player)
            await self._uow.commit()

            if current_game.is_finished():
                await self._game_view.unpin_word_mask(chat_id)
                raise GameOver(
                    (
                        "Игра завершилась! "
                        f"Победитель, {player.username}! \n"
                        "Может ещё раз? /game"
                    )
                )
