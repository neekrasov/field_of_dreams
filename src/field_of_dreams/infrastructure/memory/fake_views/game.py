from typing import List

from field_of_dreams.domain.entities.player import Player
from field_of_dreams.application.protocols.views.game import GameView


class FakeGameView(GameView):
    def __init__(self):
        self.count_events = 0

    async def send_queue(self, queue: List[Player]) -> None:
        self.count_events += 1

    async def notify_first_player_of_turn(self, player: Player) -> None:
        self.count_events += 1
