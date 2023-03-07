import aiohttp
import asyncio
import logging.config
from di import bind_by_type
from di.dependent import Dependent

from field_of_dreams.config import Settings
from field_of_dreams.core.common.exception import ApplicationException
from field_of_dreams.infrastructure.di import build_container, DIScope
from field_of_dreams.infrastructure.tgbot import TelegramBot, BasePollerImpl
from middlewares import DIMiddleware
from views.game import GameView, GameViewImpl
from handlers.exceptions import application_exception_handler
from handlers import game, on_chat_join

logger = logging.getLogger()


async def serve(token: str, timeout: int):
    session = aiohttp.ClientSession()
    bot = TelegramBot(session, token)
    poller = BasePollerImpl(session, bot, timeout)
    bot.add_exception_hander(
        ApplicationException, application_exception_handler
    )
    container = build_container()

    async with container.enter_scope(DIScope.APP) as di_state:
        bot.add_middleware(DIMiddleware(container, di_state, bot))
        container.bind(
            bind_by_type(
                Dependent(lambda *args: GameViewImpl(bot), scope=DIScope.APP),
                GameView,
            ),
        )
        game.setup_handlers(bot)
        on_chat_join.setup_handlers(bot)

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
