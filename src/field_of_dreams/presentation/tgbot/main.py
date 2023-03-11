import asyncio
import logging.config
from di.dependent import Dependent
from di.executors import AsyncExecutor

from field_of_dreams.config import Settings
from field_of_dreams.core.common.exception import (
    ApplicationException,
    GameOver,
    QueueAccessError,
)
from field_of_dreams.infrastructure.di.container import (
    DIScope,
    build_container,
    build_telegram_bot,
    build_poller,
)
from middlewares import DIMiddleware
from handlers import game, base, exc, stats

logger = logging.getLogger()


async def serve():
    container = build_container()
    di_scopes = [DIScope.APP, DIScope.REQUEST]
    bot_solved = container.solve(
        Dependent(build_telegram_bot, scope=DIScope.APP),
        scopes=di_scopes,
    )
    poller_solved = container.solve(
        Dependent(build_poller, scope=DIScope.APP),
        scopes=di_scopes,
    )
    executor = AsyncExecutor()
    async with container.enter_scope(DIScope.APP) as di_state:
        bot = await bot_solved.execute_async(executor, di_state)
        poller = await poller_solved.execute_async(executor, di_state)

        bot.add_middleware(DIMiddleware(container, di_state, bot))

        bot.add_exception_hander(GameOver, exc.game_over_exception_handler)
        bot.add_exception_hander(
            ApplicationException, exc.application_exception_handler
        )
        bot.add_exception_hander(
            QueueAccessError, exc.queue_access_exception_handler
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
