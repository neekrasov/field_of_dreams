import aiohttp
import json
from typing import List, Callable, Type, Optional, Dict, Awaitable

from .protocols import Bot, Middleware, Filter
from .handler import UpdateHandler
from .states import GameState
from .types import Update, User, Message


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
        self._states: Dict[int, GameState] = {}

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

    def set_state(self, chat_id: int, state: GameState):
        self._states[chat_id] = state

    def get_state(self, chat_id: int) -> Optional[GameState]:
        return self._states.get(chat_id)

    def _set_state_in_update(self, update: Update):
        if update.callback_query is not None:
            update.state = self._states.get(  # type: ignore
                update.callback_query.message.chat.id  # type: ignore
            )
        elif update.message is not None:
            update.state = self._states.get(update.message.chat.id)  # type: ignore  # noqa

    def add_exception_hander(
        self,
        exception_type: Type[Exception],
        handler: Callable[..., Awaitable],
    ):
        self._exc_handlers[exception_type] = handler

    async def handle_update(self, update: Update):
        self._set_state_in_update(update)

        for handler in self._handlers:
            if all(filter.filter(update) for filter in handler.filters):
                await handler.handle(update)
                break

    async def send_message(
        self, chat_id: int, text: str, reply_markup: Optional[dict] = None
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
            return Message(**json.loads(data)["result"])

    async def get_me(self) -> User:
        url = f"{self._url}getMe"
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return User(**json.loads(data)["result"])

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
            return Message(**json.loads(data)["result"])

    async def answer_callback_query(self, callback_query_id: int, text: str):
        url = f"{self._url}answerCallbackQuery"
        async with self._session.get(
            url,
            params={
                "callback_query_id": callback_query_id,
                "text": text,
            },
        ) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    @property
    def url(self):
        return self._url
