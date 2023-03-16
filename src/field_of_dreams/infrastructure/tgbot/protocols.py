import enum
from typing import Protocol, Callable, List, Awaitable, Optional, Any, Type

from .types import Update, Message, Chat, User, ChatMember
from .timer import Timer


class State:
    def to_dict(self) -> dict:
        raise NotADirectoryError

    @property
    def data(self) -> dict:
        raise NotImplementedError

    @property
    def state(self) -> enum.Enum:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError


class Storage(Protocol):
    async def get_state(self, chat_id: int) -> Optional[State]:
        raise NotImplementedError

    async def set_state(self, chat_id: int, state: State):
        raise NotImplementedError


class Filter(Protocol):
    def filter(self, update: Update) -> bool:
        raise NotImplementedError


class Middleware(Protocol):
    def __init__(self, bot: "Bot") -> None:
        raise NotImplementedError

    async def __call__(
        self, update: Update, handler: Callable[..., Awaitable]
    ):
        raise NotImplementedError


class Bot(Protocol):
    def add_handler(self, handler: Callable, filters: List[Filter]):
        raise NotImplementedError

    def add_middleware(self, middleware: Middleware):
        raise NotImplementedError

    async def handle_update(self, update: Update):
        raise NotImplementedError

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[dict] = None,
        parse_mode: str = "HTML",
    ) -> Message:
        raise NotImplementedError

    async def answer_callback_query(
        self, callback_query_id: int, text: str, show_alert: bool = True
    ):
        raise NotImplementedError

    async def pin_message(self, chat_id: int, message_id: int) -> None:
        raise NotImplementedError

    async def unpin_message(self, chat_id: int, message_id: int) -> None:
        raise NotImplementedError

    async def get_chat(self, chat_id: int) -> Chat:
        raise NotImplementedError

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        raise NotImplementedError

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> Optional[Message]:
        raise NotImplementedError

    async def get_me(self) -> User:
        raise NotImplementedError

    async def get_chat_administrators(self, chat_id: int) -> List[ChatMember]:
        raise NotImplementedError

    def get_state(self, chat_id: int) -> Any:
        raise NotImplementedError

    def set_state(self, chat_id: int, state: Any):
        raise NotImplementedError

    def get_timer(self, chat_id: int) -> Optional[Timer]:
        raise NotImplementedError

    def get_or_create_timer(self, chat_id: int) -> Timer:
        raise NotImplementedError

    def create_timer(self, chat_id: int) -> Timer:
        raise NotImplementedError

    def add_exception_hander(
        self,
        exception_type: Type[Exception],
        handler: Callable[..., Awaitable],
    ):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError


class Poller(Protocol):
    async def start_polling(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError
