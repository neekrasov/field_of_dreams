from dataclasses import dataclass
from datetime import timedelta
import logging

from ..entities.chat import ChatID
from ..entities.user import UserID
from ..common import Handler, UnitOfWork, ApplicationException, GatewayError
from ..protocols.gateways import (
    GameGateway,
    WordGateway,
    UserGateway,
    ChatGateway,
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
        chat_gateway: ChatGateway,
        uow: UnitOfWork,
    ):
        self._game_gateway = game_gateway
        self._word_gateway = word_gateway
        self._user_gateway = user_gateway
        self._chat_gateway = chat_gateway
        self._uow = uow

    async def execute(self, command: CreateGameCommand) -> None:
        chat_id = command.chat_id
        chat = await self._chat_gateway.get_chat_by_id(chat_id)
        if not chat:
            raise ApplicationException(
                (
                    "Прежде чем начать игру, познакомьтесь со мной"
                    " - введите команду /start."
                )
            )

        user_id = command.author_id
        try:
            await self._user_gateway.create_user(user_id, command.author_name)
        except GatewayError:
            logger.info("User {} already exists".format(user_id))
            pass

        exists = await self._game_gateway.get_current_game(chat_id)
        if exists:
            raise ApplicationException(
                "Игра уже началась. Дождитесь завершения прошлой игры."
            )

        word = await self._word_gateway.get_random_word()
        if word is None:
            raise ApplicationException("Нет доступных слов.")

        await self._game_gateway.create_game(
            chat_id=command.chat_id,
            word_id=word.id,  # type: ignore
            interval=command.max_turn_time,
            author_id=user_id,
        )
        await self._uow.commit()
