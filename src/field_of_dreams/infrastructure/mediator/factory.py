from field_of_dreams.core.common import UnitOfWork
from field_of_dreams.core.protocols.gateways.chat import ChatGateway
from field_of_dreams.core.protocols.gateways.game import GameGateway
from field_of_dreams.core.protocols.gateways.user import UserGateway
from field_of_dreams.core.protocols.gateways.word import WordGateway
from field_of_dreams.core.protocols.gateways.player import (
    PlayerGateway,
)
from field_of_dreams.core.protocols.views.game import GameView
from field_of_dreams.core.handlers.add_player import (
    AddPlayerHandler,
    AddPlayerCommand,
)
from field_of_dreams.core.handlers.create_game import (
    CreateGameHandler,
    CreateGameCommand,
)
from field_of_dreams.core.handlers.join_chat import (
    JoinToChatHandler,
    JoinToChatCommand,
)
from field_of_dreams.core.handlers.start_game import (
    StartGameHandler,
    StartGameCommand,
)
from field_of_dreams.core.handlers.check_user_queue import (
    CheckUserQueueHandler,
    CheckUserQueueCommand,
)
from field_of_dreams.core.handlers.letter_turn import (
    LetterTurnCommand,
    LetterTurnHandler,
)
from field_of_dreams.core.handlers.get_current_player import (
    GetCurrentPlayerCommand,
    GetCurrentPlayerHandler,
)
from field_of_dreams.core.handlers.idle_turn import (
    IdleTurnCommand,
    IdleTurnHandler,
)
from .mediator import MediatorImpl, Mediator


def build_mediator(
    chat_gateway: ChatGateway,
    game_gateway: GameGateway,
    user_gateway: UserGateway,
    word_gateway: WordGateway,
    player_gateway: PlayerGateway,
    uow: UnitOfWork,
    game_view: GameView,
) -> Mediator:
    mediator = MediatorImpl()

    mediator.bind(
        AddPlayerCommand,
        AddPlayerHandler(player_gateway, user_gateway, game_gateway, uow),
    )
    mediator.bind(
        CreateGameCommand,
        CreateGameHandler(
            game_gateway, word_gateway, user_gateway, chat_gateway, uow
        ),
    )
    mediator.bind(JoinToChatCommand, JoinToChatHandler(chat_gateway, uow))
    mediator.bind(
        StartGameCommand,
        StartGameHandler(
            game_gateway,
            player_gateway,
            user_gateway,
            game_view,
            uow,
        ),
    )
    mediator.bind(
        LetterTurnCommand,
        LetterTurnHandler(game_gateway, player_gateway, game_view, uow),
    )
    mediator.bind(
        CheckUserQueueCommand,
        CheckUserQueueHandler(game_gateway, player_gateway, game_view, uow),
    )
    mediator.bind(
        GetCurrentPlayerCommand, GetCurrentPlayerHandler(game_gateway, uow)
    )
    mediator.bind(
        IdleTurnCommand, IdleTurnHandler(game_gateway, player_gateway, uow)
    )
    return mediator
