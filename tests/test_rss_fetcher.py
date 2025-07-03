# tests/test_rss_fetcher.py
import pytest
from football_news.fetchers.rss_fetcher import run_once


@pytest.mark.asyncio
async def test_run_once():
    await run_once()
