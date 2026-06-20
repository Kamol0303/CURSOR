import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

_redis: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def is_jti_denied(jti: str) -> bool:
    r = await get_redis()
    return bool(await r.exists(f"jwt:deny:{jti}"))


async def deny_jti(jti: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"jwt:deny:{jti}", ttl_seconds, "1")


async def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    """Returns True if within limit, False if exceeded."""
    r = await get_redis()
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()
    count = results[0]
    return int(count) <= limit


async def store_nonce(api_key: str, nonce: str, ttl_seconds: int = 300) -> bool:
    """Returns False if nonce already seen (replay)."""
    r = await get_redis()
    key = f"api:nonce:{api_key}:{nonce}"
    if await r.exists(key):
        return False
    await r.setex(key, ttl_seconds, "1")
    return True


async def cache_set(key: str, value: Any, ttl: int) -> None:
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value))


async def cache_get(key: str) -> Any | None:
    r = await get_redis()
    val = await r.get(key)
    return json.loads(val) if val else None
