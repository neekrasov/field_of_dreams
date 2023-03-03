from typing import Protocol, List

from field_of_dreams.domain.entities.game import GameID
from field_of_dreams.domain.entities.player import Player


class PlayerGateway(Protocol):
    async def add_player(self, player: Player):
        raise NotImplementedError

    async def get_players(self, game_id: GameID) -> List[Player]:
        raise NotImplementedError
