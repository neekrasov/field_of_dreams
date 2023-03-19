import asyncio
import logging.config
from aiohttp.client import ClientResponseError

from field_of_dreams.config import Settings
from field_of_dreams.core.common import exception as core_exc
from field_of_dreams.infrastructure.di import DIScope, build_container
from field_of_dreams.infrastructure.rabbitmq.factory import build_rabbit_poller
from field_of_dreams.infrastructure.tgbot.factory import build_telegram_bot
from middlewares import DIMiddleware, ThrottlingMiddleware
from handlers import game, base, exc, stats

logger = logging.getLogger()


async def serve():
    container = build_container()
    di_scopes = (DIScope.APP, DIScope.REQUEST)
    async with container.enter_scope(DIScope.APP) as di_state:
        bot = await container.execute(
            build_telegram_bot, di_state, DIScope.APP, di_scopes
        )
        poller = await container.execute(
            build_rabbit_poller, di_state, DIScope.APP, di_scopes
        )
        bot.add_middleware(ThrottlingMiddleware())
        bot.add_middleware(DIMiddleware(container, di_state, bot))
        bot.add_exception_hander(
            core_exc.GameOver, exc.game_over_exception_handler
        )
        bot.add_exception_hander(
            core_exc.ApplicationException, exc.application_exception_handler
        )
        bot.add_exception_hander(
            core_exc.QueueAccessError, exc.queue_access_exception_handler
        )
        bot.add_exception_hander(
            ClientResponseError, exc.too_many_requests_handler
        )
        bot.add_exception_hander(
            core_exc.ThrottlingException, exc.throttling_exc_handler
        )
        base.setup_handlers(bot)
        game.setup_handlers(bot)
        stats.setup_handlers(bot)

        try:
            logger.info("Serve bot")
            await poller.start_polling()
        finally:
            logger.info("Shutting down bot")
            await poller.stop()


if __name__ == "__main__":
    settings = Settings()
    logging.config.fileConfig(settings.logging_config_path.strip())
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
