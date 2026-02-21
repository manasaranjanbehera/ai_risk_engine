# app/infrastructure/cache/redis_client.py

import redis.asyncio as redis

from app.config.settings import settings


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    async def set_idempotency_key(self, key: str, ttl: int = 3600):
        return await self.client.set(key, "1", ex=ttl, nx=True)

    async def exists(self, key: str):
        return await self.client.exists(key)

    async def set_cache(self, key: str, value: str, ttl: int = 300):
        await self.client.set(key, value, ex=ttl)

    async def get_cache(self, key: str):
        return await self.client.get(key)

    async def rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
    ):
        current = await self.client.incr(key)
        if current == 1:
            await self.client.expire(key, window)

        return current <= limit
