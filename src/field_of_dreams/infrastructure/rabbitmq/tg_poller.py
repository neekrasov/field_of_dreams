import asyncio
import json
import logging
import aio_pika
import typing
from aio_pika.abc import AbstractRobustConnection

from ..tgbot.protocols import Bot, Poller
from ..tgbot.types import Update

logger = logging.getLogger()


class RabbitMQPoller(Poller):
    def __init__(self, bot: Bot, rabbitmq_url: str, rabbitmq_queue: str):
        self._bot = bot
        self._rabbitmq_url = rabbitmq_url
        self._rabbitmq_queue = rabbitmq_queue
        self._connection: typing.Optional[AbstractRobustConnection] = None

    async def start_polling(self):
        connection = await aio_pika.connect_robust(self._rabbitmq_url)
        async with connection.channel() as channel:
            queue = await channel.declare_queue(
                self._rabbitmq_queue, durable=True
            )
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        async with message.process():
                            task = asyncio.create_task(
                                self._bot.handle_update(
                                    Update(**json.loads(message.body))
                                )
                            )
                            task.add_done_callback(self.handle_task)
                    except asyncio.TimeoutError:
                        message.nack(requeue=True)
                    except Exception as e:
                        logger.exception(f"Error while processing update: {e}")
                        message.reject(requeue=False)

    def handle_task(self, future: asyncio.Future):
        if exc := future.exception():
            logger.exception("Exception in task %s", exc)

    async def stop(self):
        if self._connection:
            await self._connection.close()
        logger.info("Poller stopped")
