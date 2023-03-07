import aiohttp
import asyncio
import logging
import json
import traceback
from typing import Optional

from .protocols import Bot, Poller
from .types import Update

logger = logging.getLogger()


class BasePollerImpl(Poller):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        bot: Bot,
        timeout: int = 30,
    ):
        self._session = session
        self._timeout = timeout
        self._bot = bot
        self._is_polling = False

    async def _get_updates(self, offset: Optional[int] = None):
        url = f"{self._bot.url}getUpdates?timeout={self._timeout}"
        if offset:
            url += f"&offset={offset}"
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)["result"]

    async def start_polling(self):
        offset = None
        self._is_polling = True
        while self._is_polling:
            try:
                updates = await self._get_updates(offset)
                updates = [Update(**update) for update in updates]
                for update in updates:
                    offset = update.update_id + 1
                    asyncio.create_task(self._bot.handle_update(update))
            except Exception as e:
                logger.info(traceback.format_exc())
                logger.info("Error while polling for updates: {}".format(e))
                await asyncio.sleep(5)

    async def stop(self):
        self._is_polling = False
        await self._session.close()
