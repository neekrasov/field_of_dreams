from typing import Protocol

from field_of_dreams.domain.entities.player import Player


class PlayerGateway(Protocol):
    def add_player(self, player: Player):
        raise NotImplementedError
