import asyncio
import aio_pika
import aiohttp
import logging
import typing
import json


logger = logging.getLogger()


class RabbitMQUpdatePublisher:
    def __init__(
        self,
        rabbitmq_queue: str,
        connection: aio_pika.abc.AbstractRobustConnection,
        channel: aio_pika.abc.AbstractRobustChannel,
    ):
        self._rabbitmq_queue = rabbitmq_queue
        self._connection = connection
        self._channel = channel

    async def publish_update(self, update: dict):
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(update).encode()),
            routing_key=self._rabbitmq_queue,
        )

    async def close(self):
        await self._connection.close()


class TelegramSubscriber:
    def __init__(
        self,
        token: str,
        parse_timeout: int,
        publisher: RabbitMQUpdatePublisher,
        session: aiohttp.ClientSession,
    ):
        self._token = token
        self._publisher = publisher
        self._session = session
        self._parse_timeout = parse_timeout
        self._url: str = f"https://api.telegram.org/bot{self._token}"

    async def _get_updates(self, offset: typing.Optional[int] = None):
        url = f"{self._url}/getUpdates?timeout={self._parse_timeout}"
        if offset:
            url += f"&offset={offset}"
        async with self._session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return json.loads(data)

    async def start_polling(self):
        offset = None
        self._is_polling = True
        while self._is_polling:
            try:
                updates = await self._get_updates(offset)
                if updates["ok"]:
                    updates = updates["result"]
                    for update in updates:
                        offset = update["update_id"] + 1
                        await self.process_update(update)
            except Exception as e:
                logging.error(f"Error while polling for updates: {e}")
                await asyncio.sleep(5)

    async def process_update(self, update: dict):
        try:
            await self._publisher.publish_update(update)
        except Exception as e:
            logging.error(f"Failed to publish update to RabbitMQ: {e}")

    async def stop(self):
        self._is_polling = False
        await self._session.close()
        await self._publisher.close()
