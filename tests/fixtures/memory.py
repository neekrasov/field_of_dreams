import uuid
import pytest
from typing import Dict, List
from datetime import timedelta, datetime

from field_of_dreams.domain.entities.game import Game, GameID, GameState
from field_of_dreams.domain.entities.word import Word, WordID
from field_of_dreams.domain.entities.chat import Chat, ChatID
from field_of_dreams.domain.entities.user import User, UserID
from field_of_dreams.domain.entities.player import (
    Player,
    PlayerID,
    PlayerState,
)
from field_of_dreams.infrastructure.memory.fake_gateways.game import (
    InMemoryGameGateway,
    GameGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.word import (
    InMemoryWordGateway,
    WordGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.chat import (
    InMemoryChatGateway,
    ChatGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.user import (
    InMemoryUserGateway,
    UserGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.player import (
    InMemoryPlayerGateway,
    PlayerGateway,
)
from field_of_dreams.infrastructure.memory.fake_uow import (
    FakeUnitOfWork,
    UnitOfWork,
)
from field_of_dreams.infrastructure.memory.fake_views.game import (
    FakeGameView,
    GameView,
)
from field_of_dreams.infrastructure.memory.fake_gateways.player_turn import (
    InMemoryPlayerTurnGateway,
    PlayerTurnGateway,
)


@pytest.fixture(scope="class")
def fake_words() -> Dict[WordID, Word]:
    return {
        WordID(1): Word("word1", "question1", 1),
        WordID(2): Word("word2", "question2", 2),
    }


@pytest.fixture(scope="class")
def fake_users() -> Dict[UserID, User]:
    return {
        UserID(1): User(1, "user1"),
        UserID(2): User(2, "user2"),
        UserID(3): User(3, "user3"),
    }


@pytest.fixture(scope="class")
def fake_chats() -> Dict[ChatID, Chat]:
    return {
        ChatID(1): Chat("chat1", 1),
        ChatID(2): Chat("chat2", 2),
        ChatID(3): Chat("chat3", 3),
    }


@pytest.fixture(scope="class")
def fake_players_ids() -> List[PlayerID]:
    return [PlayerID(uuid.uuid4()), PlayerID(uuid.uuid4())]


@pytest.fixture(scope="class")
def fake_games(
    fake_chats: Dict[ChatID, Chat],
    fake_words: Dict[WordID, Word],
    fake_users: Dict[UserID, User],
) -> Dict[GameID, Game]:
    chats_ids = list(fake_chats.keys())
    words_ids = list(fake_words.keys())
    users_ids = list(fake_users.keys())
    first_game_id = GameID(uuid.uuid4())
    seconds_game_id = GameID(uuid.uuid4())
    return {
        first_game_id: Game(
            chats_ids[0],
            words_ids[0],
            id=first_game_id,
            author_id=users_ids[0],
            interval=timedelta(seconds=10),
            state=GameState.FINISHED,
        ),
        seconds_game_id: Game(
            chats_ids[1],
            words_ids[1],
            id=seconds_game_id,
            author_id=users_ids[1],
            interval=timedelta(seconds=20),
            state=GameState.STARTED,
        ),
    }


@pytest.fixture(scope="class")
def fake_players(
    fake_games: Dict[GameID, Game],
    fake_users: Dict[UserID, User],
    fake_players_ids: List[PlayerID],
) -> Dict[PlayerID, Player]:
    games_ids = list(fake_games.keys())
    users_ids = list(fake_users.keys())
    return {
        fake_players_ids[0]: Player(
            games_ids[0],
            users_ids[0],
            state=PlayerState.LOSER,
            id=fake_players_ids[0],
            joined_at=datetime.utcnow(),
        ),
        fake_players_ids[1]: Player(
            games_ids[1],
            users_ids[1],
            state=PlayerState.PLAYING,
            id=fake_players_ids[1],
            joined_at=datetime.utcnow(),
        ),
    }


@pytest.fixture(scope="class")
def fake_uow() -> UnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture(scope="class")
def word_gateway(fake_words: Dict[WordID, Word]) -> WordGateway:
    return InMemoryWordGateway(fake_words)


@pytest.fixture(scope="class")
def game_gateway(fake_games: Dict[GameID, Game]) -> GameGateway:
    return InMemoryGameGateway(fake_games)


@pytest.fixture(scope="class")
def player_gateway(fake_players: Dict[PlayerID, Player]) -> PlayerGateway:
    return InMemoryPlayerGateway(fake_players)


@pytest.fixture(scope="class")
def chat_gateway(fake_chats: Dict[ChatID, Chat]) -> ChatGateway:
    return InMemoryChatGateway(fake_chats)


@pytest.fixture(scope="class")
def user_gateway(fake_users: Dict[UserID, User]) -> UserGateway:
    return InMemoryUserGateway(fake_users)


@pytest.fixture(scope="class")
def game_view() -> GameView:
    return FakeGameView()


@pytest.fixture(scope="class")
def player_turn_gateway() -> PlayerTurnGateway:
    return InMemoryPlayerTurnGateway({})
