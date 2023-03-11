from dataclasses import dataclass

from ..entities.user import UserID
from ..entities.chat import ChatID
from ..common import Handler, UnitOfWork, ApplicationException, GatewayError
from ..protocols.gateways.player import PlayerGateway
from ..protocols.gateways.user import UserGateway
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.user_stats import UserStatsGateway


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
        stats_gateway: UserStatsGateway,
        uow: UnitOfWork,
    ):
        self._player_gateway = player_gateway
        self._user_gateway = user_gateway
        self._game_gateway = game_gateway
        self._stats_gateway = stats_gateway
        self._uow = uow

    async def execute(self, command: AddPlayerCommand):
        user_id = command.user_id
        chat_id = command.chat_id

        try:
            await self._user_gateway.create_user(user_id, command.username)
        except GatewayError:
            pass

        try:
            await self._stats_gateway.create_user_stats(chat_id, user_id)
        except GatewayError:
            pass

        game = await self._game_gateway.get_current_game(chat_id)
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
