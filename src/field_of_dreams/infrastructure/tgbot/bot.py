import aiohttp
import json
from typing import List, Callable, Type, Optional, Dict, Awaitable

from .protocols import Bot, Middleware, Filter
from .handler import UpdateHandler


class TelegramBot(Bot):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: str,
    ):
        self._token = token
        self._url = f"https://api.telegram.org/bot{self._token}/"
        self._session = session
        self._handlers: List[UpdateHandler] = []
        self._middlewares: List[Middleware] = []
        self._exc_handlers: Dict[
            Type[Exception], Callable[..., Awaitable]
        ] = {}

    def add_handler(self, handler: Callable, filters: List[Filter]):
        self._handlers.append(
            UpdateHandler(
                self,
                filters=filters,
                middlewares=self._middlewares,
                exc_handlers=self._exc_handlers,
                handler=handler,
            )
        )
        return handler

    def add_middleware(self, middleware: Middleware):
        self._middlewares.append(middleware)

    def add_exception_hander(
        self,
        exception_type: Type[Exception],
        handler: Callable[..., Awaitable],
    ):
        self._exc_handlers[exception_type] = handler

    async def handle_update(self, update: dict):
        for handler in self._handlers:
            if all(filter.filter(update) for filter in handler.filters):
                await handler.handle(update)

    async def send_message(
        self, chat_id: str, text: str, reply_markup: Optional[dict] = None
    ):
        args = [
            f"{self._url}sendMessage?chat_id={chat_id}&text={text}",
        ]
        if reply_markup:
            args.append(f"&reply_markup={json.dumps(reply_markup)}")
        url = "".join(args)

        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    async def get_me(self):
        url = f"{self._url}getMe"
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    async def edit_message(self, chat_id: int, message_id: int, text: str):
        url = f"{self._url}editMessageText"
        async with self._session.get(
            url,
            params={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
            },
        ) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    @property
    def url(self):
        return self._url
