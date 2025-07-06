"""
Very small Redis-backed token bucket.

• quota_sec – allowed requests *per second*
• quota_day – allowed requests *per UTC day*

Call the decorator on any coroutine that performs a single HTTP request.
"""

import asyncio
import time
import functools

import redis.asyncio as aioredis
from redis.exceptions import RedisError

from football_news.utils.logger import logger

redis = aioredis.from_url("redis://localhost", decode_responses=True)


def _count_keys(source_name: str):
    today = time.strftime("%Y-%m-%d")
    return f"rl:{source_name}:sec", f"rl:{source_name}:day:{today}"


def with_rate_limit(fn):
    @functools.wraps(fn)
    async def wrapper(self, *args, **kwargs):
        k_sec, k_day = _count_keys(self.cfg["name"])
        while True:
            try:
                # bump counters atomically
                results = (
                    await redis.pipeline()
                    .incr(k_sec)
                    .expire(k_sec, 1)
                    .incr(k_day)
                    .expire(k_day, 60 * 60 * 24 + 60)
                    .execute()
                )
            except RedisError as exc:
                logger.warning("Redis unavailable, skipping rate limit: %s", exc)
                break

            remaining_sec, _, remaining_day, _ = results

            if (
                remaining_sec <= self.cfg["quota_sec"]
                and remaining_day <= self.cfg["quota_day"]
            ):
                break
            await asyncio.sleep(1)  # back-off

        return await fn(self, *args, **kwargs)

    return wrapper
