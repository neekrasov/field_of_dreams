import json
import enum
from typing import Optional
from redis.asyncio import Redis

from field_of_dreams.infrastructure.tgbot.protocols import Storage, State


class GameStatus(enum.Enum):
    CREATED = enum.auto()
    PREPARING = enum.auto()
    PREPARED = enum.auto()
    STARTED = enum.auto()
    PLAYER_CHOICE = enum.auto()
    WAIT_PLAYER_CHOICE = enum.auto()
    PLAYER_LETTER_TURN = enum.auto()
    PLAYER_WORD_TURN = enum.auto()
    FINISHED = enum.auto()
    PLUG = enum.auto()


class GameState(State):
    def __init__(self, state: GameStatus, data: dict = {}):
        self._state = state
        self._data = data

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, data: dict):
        self._data = data

    @property
    def state(self) -> GameStatus:
        return self._state

    def to_dict(self) -> dict:
        return {
            "state": self._state.value,
            "data": self._data
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(state=GameStatus(data["state"]), data=data.get("data", {}))


class RedisStorage(Storage):
    def __init__(self, redis: Redis, chat_prefix: str):
        self._redis = redis
        self._chat_prefix = chat_prefix

    async def get_state(self, chat_id: int) -> Optional[GameState]:
        temp = await self._redis.get(self._chat_prefix + str(chat_id))
        if temp:
            return GameState.from_dict(json.loads(temp))
        return None

    async def set_state(self, chat_id: int, state: State):
        await self._redis.set(
            self._chat_prefix + str(chat_id), json.dumps(state.to_dict())
        )
