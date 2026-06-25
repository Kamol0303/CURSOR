"""In-memory Redis substitute for local dev without Redis server."""

from __future__ import annotations

import json
import time
from typing import Any


class MemoryRedis:
    """Minimal async-compatible store for development login/MFA flows."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}

    def _purge_expired(self, key: str) -> None:
        item = self._store.get(key)
        if item and item[1] <= time.time():
            self._store.pop(key, None)

    async def exists(self, key: str) -> int:
        self._purge_expired(key)
        return 1 if key in self._store else 0

    async def get(self, key: str) -> str | None:
        self._purge_expired(key)
        item = self._store.get(key)
        return item[0] if item else None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def incr(self, key: str) -> int:
        self._purge_expired(key)
        current = int(self._store.get(key, ("0", time.time() + 3600))[0])
        current += 1
        self._store[key] = (str(current), time.time() + 3600)
        return current

    async def expire(self, key: str, ttl: int) -> None:
        if key in self._store:
            val, _ = self._store[key]
            self._store[key] = (val, time.time() + ttl)

    def pipeline(self) -> MemoryRedisPipeline:
        return MemoryRedisPipeline(self)


class MemoryRedisPipeline:
    def __init__(self, store: MemoryRedis) -> None:
        self._store = store
        self._ops: list[tuple[str, tuple[Any, ...]]] = []

    def incr(self, key: str) -> MemoryRedisPipeline:
        self._ops.append(("incr", (key,)))
        return self

    def expire(self, key: str, ttl: int) -> MemoryRedisPipeline:
        self._ops.append(("expire", (key, ttl)))
        return self

    async def execute(self) -> list[Any]:
        results: list[Any] = []
        for op, args in self._ops:
            if op == "incr":
                results.append(await self._store.incr(args[0]))
            elif op == "expire":
                await self._store.expire(args[0], args[1])
                results.append(True)
        self._ops.clear()
        return results


_memory_backend: MemoryRedis | None = None


def get_memory_redis() -> MemoryRedis:
    global _memory_backend
    if _memory_backend is None:
        _memory_backend = MemoryRedis()
    return _memory_backend
