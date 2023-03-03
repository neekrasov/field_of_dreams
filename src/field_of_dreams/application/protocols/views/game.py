from typing import Protocol, List

from field_of_dreams.domain.entities.player import Player


class GameView(Protocol):
    async def send_queue(self, queue: List[Player]) -> None:
        raise NotImplementedError

    async def notify_first_player_of_turn(self, player: Player) -> None:
        raise NotImplementedError
