import redis.asyncio as aioredis
from app.config import settings

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

async def get_from_cache(key: str):
    r = await get_redis()
    return await r.get(key)

async def set_cache(key: str, value: str, ttl: int = 3600):
    r = await get_redis()
    await r.set(key, value, ex=ttl)

async def incr_click(code: str):
    r = await get_redis()
    return await r.incr(f"clicks:{code}")

async def get_click_count(code: str):
    r = await get_redis()
    count = await r.get(f"clicks:{code}")
    return int(count) if count else 0