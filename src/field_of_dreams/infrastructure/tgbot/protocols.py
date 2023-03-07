from typing import Protocol, Callable, List, Awaitable, Optional
from .types import Update


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
        self, chat_id: int, text: str, reply_markup: Optional[dict] = None
    ):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError


class Poller(Protocol):
    async def start_polling(self, bot: Bot):
        raise NotImplementedError
