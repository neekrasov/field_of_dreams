from dataclasses import dataclass
from datetime import timedelta

from field_of_dreams.domain.entities.game import Game
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.user import UserID
from ..common import Handler, UnitOfWork, ApplicationException
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.word import WordGateway


@dataclass(frozen=True)
class CreateGameCommand:
    author_id: UserID
    chat_id: ChatID
    max_turn_time: timedelta


class CreateGameHandler(Handler[CreateGameCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        word_gateway: WordGateway,
        uow: UnitOfWork,
    ):
        self._game_gateway = game_gateway
        self._word_gateway = word_gateway
        self._uow = uow

    async def execute(self, command: CreateGameCommand) -> None:
        async with self._uow.pipeline:
            word = await self._word_gateway.get_random_word()
            if word is None:
                raise ApplicationException("Нет доступных слов")

            exists = await self._game_gateway.get_current_game(command.chat_id)
            if exists:  # TODO: Ошибка должны отображаться во вью
                raise ApplicationException(
                    "Игра уже началась. Дождитесь завершения прошлой игры."
                )
            await self._game_gateway.add_game(
                Game(
                    command.chat_id,
                    word.id,  # type: ignore
                    command.max_turn_time,
                    command.author_id,
                )
            )
            await self._uow.commit()
