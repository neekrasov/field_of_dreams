import asyncio
import json
import traceback
import logging
import aio_pika
import typing
from aio_pika.abc import AbstractRobustConnection

from ..tgbot.protocols import Bot, Poller
from ..tgbot.types import Update

logger = logging.getLogger()


class RabbitMQPoller(Poller):
    def __init__(
        self,
        bot: Bot,
        rabbitmq_url: str,
        rabbitmq_queue: str,
        timeout: int = 30,
    ):
        self._bot = bot
        self._rabbitmq_url = rabbitmq_url
        self._rabbitmq_queue = rabbitmq_queue
        self._timeout = timeout
        self._is_polling = False
        self._connection: typing.Optional[AbstractRobustConnection] = None

    async def start_polling(self):
        connection = await aio_pika.connect_robust(self._rabbitmq_url)
        channel = await connection.channel()
        queue = await channel.declare_queue(self._rabbitmq_queue, durable=True)

        self._is_polling = True
        while self._is_polling:
            try:
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            asyncio.create_task(
                                self._bot.handle_update(
                                    Update(**json.loads(message.body))
                                )
                            )
            except Exception as e:
                logger.info(traceback.format_exc())
                logger.info("Error while polling for updates: {}".format(e))
                await asyncio.sleep(5)

        await connection.close()

    async def stop(self):
        self._is_polling = False
