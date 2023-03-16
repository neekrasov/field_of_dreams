import aiohttp
import json
import logging
from typing import List, Callable, Type, Optional, Dict, Awaitable

from .protocols import Bot, Middleware, Filter, Storage
from .handler import UpdateHandler
from .types import Update, User, Message, Chat, ChatMember
from .timer import Timer

logger = logging.getLogger()


class TelegramBot(Bot):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        storage: Storage,
        token: str,
    ):
        self._token = token
        self._url = f"https://api.telegram.org/bot{self._token}/"
        self._session = session
        self._storage = storage
        self._handlers: List[UpdateHandler] = []
        self._middlewares: List[Middleware] = []
        self._exc_handlers: Dict[
            Type[Exception], Callable[..., Awaitable]
        ] = {}
        self._timers: Dict[int, Timer] = {}

    def add_handler(self, handler: Callable, filters: List[Filter]):
        self._handlers.append(
            UpdateHandler(
                self,
                filters=filters,
                middlewares=self._middlewares,
                exc_handlers=self._exc_handlers,
                handler=handler,
                storage=self._storage,
            )
        )
        return handler

    def add_middleware(self, middleware: Middleware):
        self._middlewares.append(middleware)

    def get_or_create_timer(self, chat_id: int) -> Timer:
        timer = self.get_timer(chat_id)
        if not timer:
            return self.create_timer(chat_id)
        return timer

    def get_timer(self, chat_id: int) -> Optional[Timer]:
        return self._timers.get(chat_id)

    def create_timer(self, chat_id: int) -> Timer:
        timer = Timer()
        self._timers[chat_id] = timer
        return timer

    async def set_update_state(self, update: Update):
        if callback := update.callback_query:
            message = callback.message
        elif message := update.message:
            message = message

        if not message:
            return
        cur_state = await self._storage.get_state(message.chat.id)
        if cur_state:
            update.set_state(cur_state.state)

    def add_exception_hander(
        self,
        exception_type: Type[Exception],
        handler: Callable[..., Awaitable],
    ):
        self._exc_handlers[exception_type] = handler

    async def handle_update(self, update: Update):
        await self.set_update_state(update)
        logger.info("Current state: %s", update.state)
        for handler in self._handlers:
            if all(filter.filter(update) for filter in handler.filters):
                await handler.handle(update)
                break

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[dict] = None,
        parse_mode: str = "HTML",
    ) -> Message:
        url = f"{self._url}sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        if parse_mode:
            params["parse_mode"] = parse_mode

        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.text()
            return Message(**json.loads(data)["result"])

    async def get_me(self) -> User:
        url = f"{self._url}getMe"
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return User(**json.loads(data)["result"])

    async def get_chat_administrators(self, chat_id: int) -> List[ChatMember]:
        url = f"{self._url}getChatAdministrators"
        async with self._session.get(
            url, params={"chat_id": chat_id}
        ) as response:
            response.raise_for_status()
            data = await response.text()
            members = json.loads(data)["result"]
            if not members:
                return []
            return [ChatMember(**member) for member in members]

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> Optional[Message]:
        url = f"{self._url}editMessageText"
        async with self._session.get(
            url,
            params={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode,
            },
        ) as response:
            try:
                response.raise_for_status()
                data = await response.text()
                return Message(**json.loads(data)["result"])
            except aiohttp.client_exceptions.ClientResponseError as e:
                logger.info(e)
            return None

    async def answer_callback_query(
        self, callback_query_id: int, text: str, show_alert: bool = True
    ):
        url = f"{self._url}answerCallbackQuery"
        async with self._session.get(
            url,
            params={
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": 1 if show_alert else 0,
            },
        ) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    async def pin_message(self, chat_id: int, message_id: int) -> None:
        async with self._session.get(
            f"{self._url}pinChatMessage",
            params={"chat_id": chat_id, "message_id": message_id},
        ):
            pass

    async def unpin_message(self, chat_id: int, message_id: int) -> None:
        async with self._session.get(
            f"{self._url}unpinChatMessage",
            params={"chat_id": chat_id, "message_id": message_id},
        ):
            pass

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        async with self._session.get(
            f"{self._url}deleteMessage",
            params={"chat_id": chat_id, "message_id": message_id},
        ):
            pass

    async def get_chat(self, chat_id: int) -> Chat:
        async with self._session.get(
            f"{self._url}getChat", params={"chat_id": chat_id}
        ) as response:
            response.raise_for_status()
            data = await response.text()
            return Chat(**json.loads(data)["result"])

    @property
    def url(self):
        return self._url
