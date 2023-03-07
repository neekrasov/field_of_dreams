import pytest
from typing import Dict, List

from field_of_dreams.domain.entities.user import User, UserID
from field_of_dreams.domain.entities.game import Game, GameID
from field_of_dreams.domain.entities.chat import Chat, ChatID
from field_of_dreams.domain.entities.player import Player, PlayerID
from field_of_dreams.application.protocols.gateways.game import GameGateway
from field_of_dreams.application.protocols.gateways.word import WordGateway
from field_of_dreams.application.protocols.gateways.player import PlayerGateway
from field_of_dreams.application.protocols.gateways.user import UserGateway
from field_of_dreams.application.protocols.gateways.chat import ChatGateway
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from field_of_dreams.application.protocols.views.game import GameView
from field_of_dreams.application.common import (
    UnitOfWork,
    ApplicationException,
)
from field_of_dreams.application.handlers.create_game import (
    CreateGameHandler,
    CreateGameCommand,
)
from field_of_dreams.application.handlers.add_player import (
    AddPlayerHandler,
    AddPlayerCommand,
)
from field_of_dreams.application.handlers.join_chat import (
    JoinToChatHandler,
    JoinToChatCommand,
)
from field_of_dreams.application.handlers.start_game import (
    StartGameHandler,
    StartGameCommand,
)


class TestCreateGameHandler:
    @pytest.mark.asyncio
    async def test_create_game(
        self,
        game_gateway: GameGateway,
        word_gateway: WordGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_games: Dict[GameID, Game],
        fake_players_ids: List[PlayerID],
    ):
        count_games = len(fake_games)
        await CreateGameHandler(game_gateway, word_gateway, fake_uow).execute(
            CreateGameCommand(
                fake_players_ids[0], list(fake_chats.keys())[0], 15
            )
        )

        assert len(fake_games) == count_games + 1

    @pytest.mark.asyncio
    async def test_create_game_already_playing(
        self,
        game_gateway: GameGateway,
        word_gateway: WordGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_games: Dict[GameID, Game],
        fake_players_ids: List[PlayerID],
    ):
        with pytest.raises(ApplicationException):
            await CreateGameHandler(
                game_gateway, word_gateway, fake_uow
            ).execute(
                CreateGameCommand(
                    fake_players_ids[0], list(fake_chats.keys())[1], 15
                ),
            )


class TestAddPlayerHandler:
    @pytest.mark.asyncio
    async def test_add_player_new_user(
        self,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        game_gateway: GameGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_players: Dict[PlayerID, Player],
        fake_users: Dict[UserID, User],
    ):
        old_users_count = len(fake_users)
        old_players_count = len(fake_players)
        await AddPlayerHandler(
            player_gateway, user_gateway, game_gateway, fake_uow
        ).execute(AddPlayerCommand(list(fake_chats.keys())[1], 123, "test"))

        assert len(fake_users) == old_users_count + 1
        assert len(fake_players) == old_players_count + 1

    @pytest.mark.asyncio
    async def test_add_player_existing_user(
        self,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        game_gateway: GameGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_players: Dict[PlayerID, Player],
        fake_users: Dict[UserID, User],
    ):
        old_users_count = len(fake_users)
        old_players_count = len(fake_players)
        exists_user = list(fake_users.values())[2]

        await AddPlayerHandler(
            player_gateway, user_gateway, game_gateway, fake_uow
        ).execute(
            AddPlayerCommand(
                list(fake_chats.keys())[1], exists_user.id, exists_user.name
            )
        )

        assert len(fake_users) == old_users_count
        assert len(fake_players) == old_players_count + 1

    @pytest.mark.asyncio
    async def test_add_player_already_existing_player(
        self,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        game_gateway: GameGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_players: Dict[PlayerID, Player],
        fake_users: Dict[UserID, User],
    ):
        old_users_count = len(fake_users)
        old_players_count = len(fake_players)
        exists_user = list(fake_users.values())[1]

        await AddPlayerHandler(
            player_gateway, user_gateway, game_gateway, fake_uow
        ).execute(
            AddPlayerCommand(
                list(fake_chats.keys())[1], exists_user.id, exists_user.name
            )
        )

        assert len(fake_users) == old_users_count
        assert len(fake_players) == old_players_count

    @pytest.mark.asyncio
    async def test_add_player_not_game_exists(
        self,
        player_gateway: PlayerGateway,
        user_gateway: UserGateway,
        game_gateway: GameGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
        fake_players: Dict[PlayerID, Player],
        fake_users: Dict[UserID, User],
    ):
        with pytest.raises(ApplicationException):
            await AddPlayerHandler(
                player_gateway, user_gateway, game_gateway, fake_uow
            ).execute(
                AddPlayerCommand(list(fake_chats.keys())[0], 123, "test")
            )


class TestJoinToChatHandler:
    @pytest.mark.asyncio
    async def test_join_to_chat(
        self,
        chat_gateway: ChatGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
    ):
        old_chats_count = len(fake_chats)

        await JoinToChatHandler(chat_gateway, fake_uow).execute(
            JoinToChatCommand(ChatID(123), "test")
        )

        assert len(fake_chats) == old_chats_count + 1

    @pytest.mark.asyncio
    async def test_join_to_chat_already_joined(
        self,
        chat_gateway: ChatGateway,
        fake_uow: UnitOfWork,
        fake_chats: Dict[ChatID, Chat],
    ):
        old_chats_count = len(fake_chats)
        exists_chat = list(fake_chats.values())[1]
        await JoinToChatHandler(chat_gateway, fake_uow).execute(
            JoinToChatCommand(exists_chat.id, exists_chat.name)
        )

        assert len(fake_chats) == old_chats_count


class TestStartGameHandler:
    @pytest.mark.asyncio
    async def test_start_game(
        self,
        player_turn_gateway: PlayerTurnGateway,
        game_view: GameView,
        fake_uow: UnitOfWork,
        player_gateway: PlayerGateway,
        game_gateway: GameGateway,
        fake_chats: Dict[ChatID, Chat],
        fake_games: Dict[GameID, Game],
    ):
        game = list(fake_games.values())[1]
        await player_gateway.create_player(
            Player(
                game.id,
                123,
            )
        )
        await StartGameHandler(
            game_gateway,
            player_turn_gateway,
            player_gateway,
            game_view,
            fake_uow,
        ).execute(StartGameCommand(list(fake_chats.keys())[1]))

        assert game_view.count_events == 2
        assert game.is_active is True

    @pytest.mark.asyncio
    async def test_start_game_few_players(
        self,
        player_turn_gateway: PlayerTurnGateway,
        game_view: GameView,
        fake_uow: UnitOfWork,
        player_gateway: PlayerGateway,
        game_gateway: GameGateway,
        fake_chats: Dict[ChatID, Chat],
        fake_games: Dict[GameID, Game],
    ):
        player_gateway._players = []
        with pytest.raises(ApplicationException):
            await StartGameHandler(
                game_gateway,
                player_turn_gateway,
                player_gateway,
                game_view,
                fake_uow,
            ).execute(StartGameCommand(list(fake_chats.keys())[1]))
