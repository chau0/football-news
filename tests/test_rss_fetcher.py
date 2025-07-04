import pytest
from football_news.fetchers.rss_fetcher import run_once


@pytest.mark.asyncio
async def test_run_once():
    """Test that run_once executes without errors."""
    await run_once()
