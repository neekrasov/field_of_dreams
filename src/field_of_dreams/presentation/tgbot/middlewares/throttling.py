import time
import logging
from typing import Callable, Awaitable, Dict, Any

from field_of_dreams.infrastructure.tgbot import Middleware
from field_of_dreams.infrastructure.tgbot.types import Update
from field_of_dreams.core.common.exception import (
    ApplicationException,
    ThrottlingException,
)


logger = logging.getLogger()


def throttling(rate_limit: int = 5):
    def wrapper(handler):
        setattr(handler, "throttle", True)
        setattr(handler, "throttle_rate_limit", rate_limit)
        return handler

    return wrapper


class ThrottlingMiddleware(Middleware):
    def __init__(self) -> None:
        self._cache: Dict[Any, Any] = {}

    async def __call__(
        self,
        update: Update,
        handler: Callable[..., Awaitable],
    ):
        if message := update.message:
            if user := message.from_user:
                user_id = user.id
                username = message.from_user.username
            chat_id = message.chat.id
        else:
            return

        if hasattr(handler, "throttle"):
            key = (user_id, chat_id)
            show_exc = False
            if key not in self._cache:
                self._cache[key] = {
                    "last_update_time": time.time(),
                    "update_count": 0,
                    "notified": False,
                }
            else:
                rate_limit = getattr(handler, "throttle_rate_limit", 5)
                last_update_time = self._cache[key]["last_update_time"]

                if time.time() - last_update_time < rate_limit:
                    show_exc = True
                else:
                    self._cache[key]["notified"] = False

            self._cache[key]["last_update_time"] = time.time()
            self._cache[key]["update_count"] += 1

            if show_exc:
                if not self._cache[key]["notified"]:
                    self._cache[key]["notified"] = True
                    raise ApplicationException(
                        f"@{username}, повторный запрос можно выполнить через "
                        f"{rate_limit} секунд."
                    )
                raise ThrottlingException(f"User {user_id} is throttled")

        return handler
