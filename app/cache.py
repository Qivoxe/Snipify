import redis.asyncio as redis
from app.config import settings

redis_client: aioredis.Redis = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.Redis(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

async def get_from_cache(code: str) -> str:
    redis_client = await get_redis()
    return await redis_client.get(code)

async def set_cache(key: str, value: str, expire: int = 3600):
    redis_client = await get_redis()
    await redis_client.set(key, value, ex=expire)

async def incr_click(code: str) -> int:
    r = await get_redis()
    return await r.incr(f"clicks:{code}")

async def get_click_count(code: str) -> int:
    r = await get_redis()
    count = await r.get(f"clicks:{code}")
    return int(count) if count else 0    