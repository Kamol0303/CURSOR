#!/usr/bin/env python3
"""Simple load test for TaMoR public and health endpoints."""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx

DEFAULT_URL = "http://localhost:8000"


async def run_load(base_url: str, concurrency: int, requests_per_worker: int) -> None:
    latencies: list[float] = []
    errors = 0

    async def worker(worker_id: int) -> None:
        nonlocal errors
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            for i in range(requests_per_worker):
                start = time.perf_counter()
                try:
                    if i % 3 == 0:
                        res = await client.get("/health")
                    else:
                        res = await client.get("/api/v1/public/verify/TAMOR-DEMO-NOTFOUND")
                    res.raise_for_status()
                    latencies.append((time.perf_counter() - start) * 1000)
                except Exception:
                    errors += 1

    started = time.perf_counter()
    await asyncio.gather(*[worker(w) for w in range(concurrency)])
    elapsed = time.perf_counter() - started
    total = concurrency * requests_per_worker

    print(f"Total requests: {total}")
    print(f"Errors: {errors}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"RPS: {total / elapsed:.1f}")
    if latencies:
        print(f"p50: {statistics.median(latencies):.1f}ms")
        print(f"p95: {sorted(latencies)[int(len(latencies) * 0.95) - 1]:.1f}ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="TaMoR load test")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("-c", "--concurrency", type=int, default=10)
    parser.add_argument("-n", "--requests", type=int, default=20, help="Requests per worker")
    args = parser.parse_args()
    asyncio.run(run_load(args.url, args.concurrency, args.requests))


if __name__ == "__main__":
    main()
