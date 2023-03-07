from typing import Protocol, Callable, List, Awaitable, Optional

from .types import Update, Message, Chat, User


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

    async def pin_message(self, chat_id: int, message_id: int) -> None:
        raise NotImplementedError

    async def get_chat(self, chat_id: int) -> Chat:
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

    @property
    def url(self):
        raise NotImplementedError


class Poller(Protocol):
    async def start_polling(self, bot: Bot):
        raise NotImplementedError
