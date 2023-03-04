import aiohttp
import asyncio
import logging.config

from field_of_dreams.infrastructure.tgbot import (
    TelegramBot,
    BasePollerImpl,
    filters,
)
from field_of_dreams.config import Settings

from handlers.echo import echo_handler
from middlewares.logging import LoggingMiddleware

logger = logging.getLogger()


async def serve(token: str, timeout: int):
    session = aiohttp.ClientSession()
    bot = TelegramBot(session, token)
    bot.add_handler(echo_handler, [filters.MessageFilter, filters.GroupFilter])
    bot.add_middleware(LoggingMiddleware())
    poller = BasePollerImpl(session, bot, timeout)
    try:
        logger.info("Serve bot")
        await poller.start_polling()
    finally:
        logger.info("Shutting down bot")
        await poller.stop()


if __name__ == "__main__":
    settings = Settings()
    logging.config.fileConfig("src/field_of_dreams/config/logging_config.ini")
    try:
        asyncio.run(
            serve(token=settings.bot.token, timeout=settings.bot.timeout)
        )
    except KeyboardInterrupt:
        pass
