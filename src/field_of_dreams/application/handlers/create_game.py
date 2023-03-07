from dataclasses import dataclass
from datetime import timedelta
import logging

from field_of_dreams.domain.entities.game import Game
from field_of_dreams.domain.entities.chat import ChatID
from field_of_dreams.domain.entities.user import UserID, User
from ..common import Handler, UnitOfWork, ApplicationException, GatewayError
from ..protocols.gateways import (
    GameGateway,
    WordGateway,
    UserGateway,
)

logger = logging.getLogger()


@dataclass(frozen=True)
class CreateGameCommand:
    author_id: UserID
    author_name: str
    chat_id: ChatID
    max_turn_time: timedelta


class CreateGameHandler(Handler[CreateGameCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        word_gateway: WordGateway,
        user_gateway: UserGateway,
        uow: UnitOfWork,
    ):
        self._game_gateway = game_gateway
        self._word_gateway = word_gateway
        self._user_gateway = user_gateway
        self._uow = uow

    async def execute(self, command: CreateGameCommand) -> None:
        user = User(command.author_id, command.author_name)
        try:
            await self._user_gateway.add_user(user)
        except GatewayError:
            logger.info("User {} already exists".format(command.author_id))
            pass

        exists = await self._game_gateway.get_current_game(command.chat_id)
        if exists and not exists.is_created:
            raise ApplicationException(
                "Игра уже началась. Дождитесь завершения прошлой игры."
            )

        word = await self._word_gateway.get_random_word()
        if word is None:
            raise ApplicationException("Нет доступных слов")

        if not exists or exists.is_created:
            await self._game_gateway.add_game(
                Game(
                    chat_id=command.chat_id,
                    word_id=word.id,  # type: ignore
                    interval=command.max_turn_time,
                    author_id=user.id,
                )
            )
        await self._uow.commit()
