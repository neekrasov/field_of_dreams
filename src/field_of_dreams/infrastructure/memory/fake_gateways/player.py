import uuid
from typing import Dict, List

from field_of_dreams.domain.entities.player import Player, PlayerID
from field_of_dreams.domain.entities.game import GameID
from field_of_dreams.application.protocols.gateways.player import PlayerGateway
from field_of_dreams.application.common import GatewayError


class InMemoryPlayerGateway(PlayerGateway):
    def __init__(self, players: Dict[PlayerID, Player]):
        self._players = players

    async def add_player(self, player: Player):
        for i in self._players.values():
            if player.user_id == i.user_id and player.game_id == i.game_id:
                raise GatewayError("Player already exists")

        player.id = PlayerID(uuid.uuid4())
        self._players[player.id] = player

    async def get_players(self, game_id: GameID) -> List[Player]:
        return [
            self._players[i]
            for i in self._players
            if self._players[i].game_id == game_id
        ]
