import asyncio
import aio_pika
import aiohttp
import logging
import logging.config

from field_of_dreams.infrastructure.rabbitmq.tg_publisher import (
    TelegramSubscriber,
    RabbitMQUpdatePublisher,
)
from field_of_dreams.config.settings import Settings

logger = logging.getLogger()


async def serve(
    bot_token: str,
    parse_timeout: int,
    rabbit_url: str,
    rabbit_queue: str,
) -> None:
    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()
    await channel.declare_queue(rabbit_queue, durable=True)
    client_session = aiohttp.ClientSession()

    publisher = RabbitMQUpdatePublisher(rabbit_queue, connection, channel)  # type: ignore # noqa
    tg_subscriber = TelegramSubscriber(
        bot_token, parse_timeout, publisher, client_session
    )

    try:
        logger.info("Serve amqp")
        await tg_subscriber.start_polling()
    finally:
        logger.info("Shutting down amqp")
        await tg_subscriber.stop()

    await tg_subscriber.start_polling()


if __name__ == "__main__":
    settings = Settings()
    logging.config.fileConfig(settings.logging_config_path.strip())
    try:
        asyncio.run(
            serve(
                bot_token=settings.bot.token,
                parse_timeout=settings.bot.timeout,
                rabbit_url=settings.rabbit.url,
                rabbit_queue=settings.rabbit.queue,
            )
        )
    except KeyboardInterrupt:
        pass
