# scripts/test_redis.py

import sys
from pathlib import Path

# Ensure project root is on the path when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.infrastructure.cache.redis_client import RedisClient

async def test():
    r = RedisClient()

    result1 = await r.set_idempotency_key("order_123")
    result2 = await r.set_idempotency_key("order_123")

    print("First insert:", result1)
    print("Second insert:", result2)

asyncio.run(test())
