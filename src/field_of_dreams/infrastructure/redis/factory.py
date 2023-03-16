from redis.asyncio import Redis

from field_of_dreams.config import Settings


def build_redis(settings: Settings) -> Redis:
    return Redis(
        host=settings.redis.host,
        port=settings.redis.port,
    )
