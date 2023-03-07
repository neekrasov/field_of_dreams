import uuid
from typing import Dict, Optional

from field_of_dreams.core.entities.game import Game, GameID
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.protocols.gateways.game import GameGateway


class InMemoryGameGateway(GameGateway):
    def __init__(self, games: Dict[GameID, Game]):
        self.games = games

    async def add_game(self, game: Game):
        game.id = GameID(uuid.uuid4())
        self.games[game.id] = game

    async def get_current_game(self, chat_id: ChatID) -> Optional[Game]:
        for game in list(self.games.values()):
            if game.chat_id == chat_id:
                if game.is_active:
                    return game
        return None
