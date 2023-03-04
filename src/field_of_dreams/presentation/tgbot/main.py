import aiohttp
import asyncio
import logging.config
from di import bind_by_type
from di.dependent import Dependent

from field_of_dreams.infrastructure.di import build_container, DIScope
from field_of_dreams.infrastructure.tgbot import (
    TelegramBot,
    BasePollerImpl,
    filters,
)
from field_of_dreams.config import Settings
from handlers.echo import echo_handler
from middlewares import (
    LoggingMiddleware,
    ExceptionsMiddleware,
    DIMiddleware,
)
from views.game import GameView, GameViewImpl

logger = logging.getLogger()


async def serve(token: str, timeout: int):
    session = aiohttp.ClientSession()
    bot = TelegramBot(session, token)
    poller = BasePollerImpl(session, bot, timeout)
    container = build_container()
    async with container.enter_scope(DIScope.APP) as di_state:
        bot.add_middleware(DIMiddleware(container, di_state, bot))
        bot.add_middleware(LoggingMiddleware(bot))
        bot.add_middleware(ExceptionsMiddleware(bot))
        container.bind(
            bind_by_type(
                Dependent(lambda *args: GameViewImpl(bot), scope=DIScope.APP),
                GameView,
            ),
        )
        bot.add_handler(
            echo_handler, [filters.MessageFilter, filters.GroupFilter]
        )

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
