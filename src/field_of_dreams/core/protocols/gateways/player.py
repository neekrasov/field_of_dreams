from typing import Protocol, Sequence, Optional

from field_of_dreams.core.entities.game import GameID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.entities.player import Player


class PlayerGateway(Protocol):
    async def create_player(self, game_id: GameID, user_id: UserID):
        raise NotImplementedError

    async def get_players(self, game_id: GameID) -> Sequence[Player]:
        raise NotImplementedError

    async def get_next_player(
        self, user_id: UserID, game_id: GameID
    ) -> Optional[Player]:
        raise NotImplementedError

    async def update_player(self, player: Player) -> None:
        raise NotImplementedError
