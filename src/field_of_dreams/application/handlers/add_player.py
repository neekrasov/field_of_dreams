from dataclasses import dataclass

from field_of_dreams.domain.entities.user import UserID, User
from field_of_dreams.domain.entities.chat import ChatID
from ..common import Handler, UnitOfWork, ApplicationException, GatewayError
from ..protocols.gateways.player import PlayerGateway
from ..protocols.gateways.user import UserGateway
from ..protocols.gateways.game import GameGateway


@dataclass(frozen=True)
class AddPlayerCommand:
    chat_id: ChatID
    user_id: UserID
    username: str


class AddPlayerHandler(Handler[AddPlayerCommand, None]):
    def __init__(
        self,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        game_gateway: GameGateway,
        uow: UnitOfWork,
    ):
        self._player_gateway = player_gateway
        self._user_gateway = user_gateway
        self._game_gateway = game_gateway
        self._uow = uow

    async def execute(self, command: AddPlayerCommand):
        user_id = command.user_id
        try:
            await self._user_gateway.add_user(User(user_id, command.username))
        except GatewayError:
            pass

        game = await self._game_gateway.get_current_game(command.chat_id)
        if not game:
            raise ApplicationException(
                (
                    "Присоединится к игре невозможно."
                    "Чтобы создать игру введи команду /game."
                )
            )

        if game and game.is_started:
            raise ApplicationException(
                "Игра уже началась, попробуйте присоединиться позже."
            )
        try:
            await self._player_gateway.create_player(game.id, user_id)  # type: ignore # noqa
        except GatewayError:
            pass

        await self._uow.commit()
