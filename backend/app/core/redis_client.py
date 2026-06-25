import json
import logging
from typing import Any

import redis.asyncio as redis

from app.core.config import settings
from app.core.memory_redis import get_memory_redis

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None
_use_memory = settings.USE_MEMORY_REDIS or settings.REDIS_URL.startswith("memory://")


async def get_redis():
    global _redis
    if _use_memory:
        return get_memory_redis()
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def is_jti_denied(jti: str) -> bool:
    try:
        r = await get_redis()
        return bool(await r.exists(f"jwt:deny:{jti}"))
    except Exception:
        if settings.ENVIRONMENT == "development":
            return False
        raise


async def deny_jti(jti: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"jwt:deny:{jti}", ttl_seconds, "1")


async def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    """Returns True if within limit, False if exceeded."""
    try:
        r = await get_redis()
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        results = await pipe.execute()
        count = results[0]
        return int(count) <= limit
    except Exception:
        if settings.ENVIRONMENT == "development":
            logger.warning("Redis unavailable — rate limit skipped (dev)")
            return True
        raise


async def store_nonce(api_key: str, nonce: str, ttl_seconds: int = 300) -> bool:
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
