import aiohttp
import asyncio
import logging.config
from di import bind_by_type
from di.dependent import Dependent

from field_of_dreams.config import Settings
from field_of_dreams.application.common.exception import ApplicationException
from field_of_dreams.infrastructure.di import build_container, DIScope
from field_of_dreams.infrastructure.persistence.sqlalchemy import models
from field_of_dreams.infrastructure.tgbot import (
    TelegramBot,
    BasePollerImpl,
    filters,
)
from views.game import GameView, GameViewImpl
from handlers.echo import echo_handler
from handlers.exceptions import application_exception_handler
from middlewares import (
    DIMiddleware,
)

logger = logging.getLogger()


async def serve(token: str, timeout: int):
    session = aiohttp.ClientSession()
    bot = TelegramBot(session, token)
    poller = BasePollerImpl(session, bot, timeout)
    bot.add_exception_hander(
        ApplicationException, application_exception_handler
    )
    models.start_mapping()
    container = build_container()
    async with container.enter_scope(DIScope.APP) as di_state:
        bot.add_middleware(DIMiddleware(container, di_state, bot))
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
