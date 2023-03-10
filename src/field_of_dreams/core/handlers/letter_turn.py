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
from ..protocols.views.game import GameView
from ..services.score import generate_random_score


@dataclass(frozen=True)
class LetterTurnCommand:
    chat_id: ChatID
    letter: str
    score_from: int
    score_to: int


class LetterTurnHandler(Handler[LetterTurnCommand, None]):
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
            already_guessed = current_game.check_already_guessed_letter(letter)
            check_answer = word.check_guess(letter)

            if already_guessed:
                await self._game_view.already_guessed_letter(
                    chat_id, letter, player.get_username()
                )
            elif check_answer:
                is_last = word.is_last_letter_remaining(
                    current_game.guessed_letters
                )
                score_per_turn = generate_random_score(
                    command.score_from, command.score_to
                )
                player.add_score(score_per_turn)
                current_game.add_guessed_letter(letter)
                if is_last:
                    current_game.finish()
                    await self._game_view.update_word_mask(
                        chat_id,
                        word.get_mask(current_game.guessed_letters),
                        word.question,
                    )
                    await self._game_view.winner_letter(
                        chat_id,
                        letter,
                        player.get_username(),
                        word.count_letter(letter),
                        score_per_turn,
                        player.get_score(),
                    )
                else:
                    await self._game_view.correct_letter(
                        chat_id,
                        letter,
                        word.count_letter(letter),
                        player.get_username(),
                        score_per_turn,
                    )
                    await self._game_view.update_word_mask(
                        chat_id,
                        word.get_mask(current_game.guessed_letters),
                        word.question,
                    )
            else:
                await self._game_view.wrong_letter(
                    chat_id, letter, player.get_username()
                )

            player.state = PlayerState.WAITING
            if not current_game.is_finished():
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
                        f"Победитель, {player.get_username()}! \n"
                        "Может ещё раз? /game"
                    )
                )
