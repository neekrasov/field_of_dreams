from field_of_dreams.application.common import UnitOfWork
from field_of_dreams.application.protocols.gateways.chat import ChatGateway
from field_of_dreams.application.protocols.gateways.game import GameGateway
from field_of_dreams.application.protocols.gateways.user import UserGateway
from field_of_dreams.application.protocols.gateways.word import WordGateway
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from field_of_dreams.application.protocols.gateways.player import (
    PlayerGateway,
)
from field_of_dreams.application.protocols.views.game import GameView
from field_of_dreams.application.handlers.add_player import (
    AddPlayerHandler,
    AddPlayerCommand,
)
from field_of_dreams.application.handlers.create_game import (
    CreateGameHandler,
    CreateGameCommand,
)
from field_of_dreams.application.handlers.join_chat import (
    JoinToChatHandler,
    JoinToChatCommand,
)
from field_of_dreams.application.handlers.start_game import (
    StartGameHandler,
    StartGameCommand,
)
from .mediator import MediatorImpl, Mediator


def build_mediator(
    chat_gateway: ChatGateway,
    game_gateway: GameGateway,
    user_gateway: UserGateway,
    word_gateway: WordGateway,
    player_turn_gateway: PlayerTurnGateway,
    player_gateway: PlayerGateway,
    uow: UnitOfWork,
    view: GameView,
) -> Mediator:
    mediator = MediatorImpl()

    mediator.bind(
        AddPlayerCommand,
        AddPlayerHandler(player_gateway, user_gateway, game_gateway, uow),
    )
    mediator.bind(
        CreateGameCommand, CreateGameHandler(game_gateway, word_gateway, uow)
    )
    mediator.bind(JoinToChatCommand, JoinToChatHandler(chat_gateway, uow))
    mediator.bind(
        StartGameCommand,
        StartGameHandler(
            game_gateway, player_turn_gateway, player_gateway, view, uow
        ),
    )
    return mediator