from dataclasses import dataclass

from ..entities.chat import ChatID
from ..entities.player import PlayerState
from ..common import (
    Handler,
    UnitOfWork,
    ApplicationException,
    GameOver,
)
from ..protocols.gateways.game import GameGateway
from ..protocols.gateways.player import PlayerGateway


@dataclass(frozen=True)
class IdleTurnCommand:
    chat_id: ChatID


class IdleTurnHandler(Handler[IdleTurnCommand, None]):
    def __init__(
        self,
        game_gateway: GameGateway,
        player_gateway: PlayerGateway,
        uow: UnitOfWork,
    ) -> None:
        self._game_gateway = game_gateway
        self._player_gateway = player_gateway
        self._uow = uow

    async def execute(self, command: IdleTurnCommand) -> None:
        async with self._uow.pipeline:
            chat_id = command.chat_id
            current_game = await self._game_gateway.get_current_game(chat_id)
            if not current_game:
                raise ApplicationException(
                    "Игра не создана. Начните игру командой /game."
                )
            player = current_game.cur_player
            if not player:
                raise ApplicationException(
                    "Не удалось обнаружить текущего игрока."
                )
            player.state = PlayerState.WAITING
            next_player = await self._player_gateway.get_next_player(
                player, current_game.id  # type: ignore
            )
            if next_player:
                next_player.state = PlayerState.PROCESSING
                current_game.set_next_player(next_player)
                await self._player_gateway.update_player(next_player)
                await self._game_gateway.update_game(current_game)
                await self._player_gateway.update_player(player)
                await self._uow.commit()
            else:
                current_game.finish()
                await self._uow.commit()
                raise GameOver(
                    (
                        f"🫤 {player.get_username()} решил пропустить ход. \n"
                        "Игра завершилась ничьёй, никто не угадал слово... \n"
                        "Попробуйте ещё раз! /game"
                    )
                )
