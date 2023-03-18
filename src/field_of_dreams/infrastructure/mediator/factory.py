from field_of_dreams.core.common import UnitOfWork
from field_of_dreams.core.services.hasher import PasswordHasher
from field_of_dreams.core.protocols.gateways.chat import ChatGateway
from field_of_dreams.core.protocols.gateways.game import GameGateway
from field_of_dreams.core.protocols.gateways.user import UserGateway
from field_of_dreams.core.protocols.gateways.word import WordGateway
from field_of_dreams.core.protocols.gateways.user_stats import UserStatsGateway
from field_of_dreams.core.protocols.gateways.admin import AdminGateway
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
from field_of_dreams.core.handlers.word_turn import (
    WordTurnCommand,
    WordTurnHandler,
)
from field_of_dreams.core.handlers.finish_game import (
    FinishGameCommand,
    FinishGameHandler,
)
from field_of_dreams.core.handlers.check_is_last import (
    CheckLastPlayerCommand,
    CheckLastPlayerHandler,
)
from field_of_dreams.core.handlers.get_chat_stats import (
    GetChatStatsCommand,
    GetChatStatsHandler,
)
from field_of_dreams.core.handlers.admin_login import (
    AdminLoginCommand,
    AdminLoginHandler,
)
from field_of_dreams.core.handlers.create_admin import (
    CreateAdminCommand,
    CreateAdminHandler,
)
from field_of_dreams.core.handlers.get_admin_by_email import (
    GetAdminByEmailCommand,
    GetAdminByEmailHandler,
)
from field_of_dreams.core.handlers.get_user_stats import (
    GetUserStatsCommand,
    GetUserStatsHandler,
)
from field_of_dreams.core.handlers.crud_word import (
    CreateWordCommand,
    UpdateWordCommand,
    DeleteWordCommand,
    GetWordCommand,
    CreateWordHandler,
    UpdateWordHandler,
    DeleteWordHandler,
    GetWordHandler,
)
from .mediator import MediatorImpl, Mediator
from field_of_dreams.config import Settings


def build_mediator(
    chat_gateway: ChatGateway,
    game_gateway: GameGateway,
    user_gateway: UserGateway,
    word_gateway: WordGateway,
    player_gateway: PlayerGateway,
    stats_gateway: UserStatsGateway,
    admin_gateway: AdminGateway,
    hasher: PasswordHasher,
    uow: UnitOfWork,
    game_view: GameView,
    settings: Settings,
) -> Mediator:
    mediator = MediatorImpl()

    mediator.bind(
        AddPlayerCommand,
        AddPlayerHandler(
            player_gateway, user_gateway, game_gateway, stats_gateway, uow
        ),
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
            game_gateway, player_gateway, user_gateway, game_view, uow
        ),
    )
    mediator.bind(
        LetterTurnCommand,
        LetterTurnHandler(
            game_gateway,
            player_gateway,
            game_view,
            stats_gateway,
            uow,
            settings.bot.random_score_from,
            settings.bot.random_score_to,
        ),
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
    mediator.bind(
        WordTurnCommand,
        WordTurnHandler(
            game_gateway,
            player_gateway,
            game_view,
            stats_gateway,
            uow,
            settings.bot.random_score_from,
            settings.bot.word_score_to,
        ),
    )
    mediator.bind(
        FinishGameCommand, FinishGameHandler(game_gateway, game_view, uow)
    )
    mediator.bind(
        CheckLastPlayerCommand,
        CheckLastPlayerHandler(game_gateway, player_gateway, uow),
    )
    mediator.bind(
        GetChatStatsCommand,
        GetChatStatsHandler(chat_gateway, stats_gateway, game_view, uow),
    )
    mediator.bind(AdminLoginCommand, AdminLoginHandler(hasher, admin_gateway))
    mediator.bind(
        CreateAdminCommand, CreateAdminHandler(hasher, admin_gateway, uow)
    )
    mediator.bind(
        GetAdminByEmailCommand, GetAdminByEmailHandler(admin_gateway)
    )
    mediator.bind(GetWordCommand, GetWordHandler(word_gateway))
    mediator.bind(CreateWordCommand, CreateWordHandler(word_gateway, uow))
    mediator.bind(UpdateWordCommand, UpdateWordHandler(word_gateway, uow))
    mediator.bind(DeleteWordCommand, DeleteWordHandler(word_gateway, uow))
    mediator.bind(
        GetUserStatsCommand,
        GetUserStatsHandler(stats_gateway, game_view, uow),
    )
    return mediator
