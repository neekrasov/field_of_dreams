import logging
from redis.asyncio import Redis

from field_of_dreams.config import Settings
from .storage import RedisStorage

logger = logging.getLogger()


def build_redis_storage(settings: Settings, redis: Redis) -> RedisStorage:
    return RedisStorage(redis, settings.redis.chat_prefix)
