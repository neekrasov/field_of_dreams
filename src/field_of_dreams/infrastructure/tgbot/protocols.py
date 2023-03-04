from typing import Protocol, Callable, List, Type


class Filter(Protocol):
    @staticmethod
    def filter(update: dict) -> bool:
        raise NotImplementedError


class Middleware(Protocol):
    async def __call__(self, update: dict, handler: Callable):
        raise NotImplementedError


class Bot(Protocol):
    def add_handler(self, handler: Callable, filters: List[Type[Filter]]):
        raise NotImplementedError

    def add_middleware(self, middleware: Middleware):
        raise NotImplementedError

    async def handle_update(self, update: dict):
        raise NotImplementedError

    async def send_message(self, chat_id: str, text: str):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError


class Poller(Protocol):
    async def start_polling(self, bot: Bot):
        raise NotImplementedError
