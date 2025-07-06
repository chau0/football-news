from __future__ import annotations

import asyncio
import httpx
import logging

log = logging.getLogger(__name__)


class BaseFetcher:
    timeout = 10
    max_retries = 2

    def __init__(self, cfg: dict):
        self.cfg = cfg

    async def _get(self, url: str, headers: dict | None = None):
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    return await client.get(url, headers=headers or {})
            except httpx.RequestError as exc:  # network error, retry
                if attempt == self.max_retries:
                    log.error("GET %s failed: %s", url, exc)
                    raise
                await asyncio.sleep(2**attempt)

    async def fetch(self) -> int:  # must return rows inserted
        raise NotImplementedError
