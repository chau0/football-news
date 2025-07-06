import asyncio
import datetime as dt
import hashlib
import os

from sqlalchemy.dialects.sqlite import insert
from football_news.fetchers.base import BaseFetcher
from football_news.middlewares.ratelimit import with_rate_limit
from football_news.storage.db import SessionLocal
from football_news.storage.models import Story
import httpx
import logging

logger = logging.getLogger(__name__)


class NewsAPIFetcher(BaseFetcher):
    def __init__(self, cfg: dict):
        super().__init__(cfg)
        # Fix URL construction - use the api_key placeholder from config
        api_key = os.environ["NEWSAPI_KEY"]
        self.url = cfg["endpoint"].format(api_key=api_key)

    @with_rate_limit
    async def _call(self):
        response = await self._get(self.url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response

    async def fetch(self) -> int:
        try:
            response = await self._call()
            data = response.json()

            # Check API response status
            if data.get("status") != "ok":
                error_msg = data.get("message", "Unknown API error")
                logger.error("NewsAPI error: %s", error_msg)
                return 0

            articles = data.get("articles", [])
            rows = []
            logger.info("Fetched %d articles from NewsAPI", len(articles))

            for art in articles:
                # Skip articles without required fields
                if not art.get("url") or not art.get("title"):
                    continue

                link = art["url"]

                # Handle publishedAt field - some articles might not have it
                published_at = art.get("publishedAt")
                if published_at:
                    try:
                        published = dt.datetime.fromisoformat(
                            published_at.replace("Z", "+00:00")
                        )
                    except ValueError:
                        logger.warning("Invalid date format for article: %s", link)
                        published = dt.datetime.now(dt.timezone.utc)
                else:
                    published = dt.datetime.now(dt.timezone.utc)

                rows.append(
                    dict(
                        id=hashlib.sha1(link.encode()).hexdigest(),
                        title=art["title"],
                        link=link,
                        source="newsapi",
                        published=published,
                        raw=art.get("content") or art.get("description", ""),
                    )
                )

            await self._bulk_insert(rows)
            return len(rows)

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error fetching from NewsAPI: %s", e)
            return 0
        except Exception as e:
            logger.error("Unexpected error fetching from NewsAPI: %s", e)
            return 0

    async def _bulk_insert(self, rows):
        if not rows:
            return
        stmt = insert(Story).values(rows).prefix_with("OR IGNORE")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._commit, stmt)

    @staticmethod
    def _commit(stmt):
        s = SessionLocal()
        try:
            s.execute(stmt)
            s.commit()
        except Exception as e:
            logger.error("Database error during bulk insert: %s", e)
            s.rollback()
        finally:
            s.close()
