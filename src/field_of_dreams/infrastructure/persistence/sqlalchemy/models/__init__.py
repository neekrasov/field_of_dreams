from .base import Base  # noqa
from .user import User, map_user_table  # noqa
from .chat import Chat, map_chat_table  # noqa
from .game import Game, map_game_table  # noqa
from .player_turn import PlayerTurn, map_player_turn_table  # noqa
from .player import Player, map_player_table  # noqa
from .word import Word, map_word_table  # noqa


def start_mapping() -> None:
    mapper_registry = Base.registry
    map_chat_table(mapper_registry)
    map_user_table(mapper_registry)
    map_player_turn_table(mapper_registry)
    map_player_table(mapper_registry)
    map_word_table(mapper_registry)
    map_game_table(mapper_registry)
