from .models import (
    map_chat_table,
    map_user_table,
    map_player_turn_table,
    map_player_table,
    map_word_table,
    map_game_table,
    Base,
)


def start() -> None:
    mapper_registry = Base.registry
    map_chat_table(mapper_registry)
    map_user_table(mapper_registry)
    map_player_turn_table(mapper_registry)
    map_player_table(mapper_registry)
    map_word_table(mapper_registry)
    map_game_table(mapper_registry)
