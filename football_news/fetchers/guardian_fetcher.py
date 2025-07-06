from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import os
import logging

from sqlalchemy.dialects.sqlite import insert
import httpx

from football_news.fetchers.base import BaseFetcher
from football_news.middlewares.ratelimit import with_rate_limit
from football_news.storage.db import SessionLocal
from football_news.storage.models import Story

logger = logging.getLogger(__name__)


class GuardianFetcher(BaseFetcher):
    def __init__(self, cfg: dict):
        super().__init__(cfg)
        # Fix URL construction - use the api_key placeholder from config
        api_key = os.environ["GUARDIAN_KEY"]
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

            # Check Guardian API response structure
            if "response" not in data:
                logger.error("Guardian API response missing 'response' field: %s", data)
                return 0

            response_data = data["response"]
            if response_data.get("status") != "ok":
                logger.error(
                    "Guardian API error status: %s", response_data.get("status")
                )
                return 0

            results = response_data.get("results", [])
            logger.info("Fetched %d articles from Guardian", len(results))

            rows = []
            for item in results:
                try:
                    row = self._to_row(item)
                    if row:  # Only add if conversion was successful
                        rows.append(row)
                except Exception as e:
                    logger.warning("Failed to process Guardian article: %s", e)
                    continue

            await self._bulk_insert(rows)
            return len(rows)

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error fetching from Guardian: %s", e)
            return 0
        except Exception as e:
            logger.error("Unexpected error fetching from Guardian: %s", e)
            return 0

    @staticmethod
    def _to_row(item: dict) -> dict | None:
        try:
            # Check required fields
            if not item.get("webUrl") or not item.get("webTitle"):
                return None

            link = item["webUrl"]

            # Handle optional fields
            published_date = item.get("webPublicationDate")
            if published_date:
                try:
                    published = dt.datetime.fromisoformat(
                        published_date.replace("Z", "+00:00")
                    )
                except ValueError:
                    logger.warning("Invalid date format for Guardian article: %s", link)
                    published = dt.datetime.now(dt.timezone.utc)
            else:
                published = dt.datetime.now(dt.timezone.utc)

            # Handle body field - it might be nested in fields
            body = ""
            if "fields" in item and "body" in item["fields"]:
                body = item["fields"]["body"]
            elif "fields" in item and "bodyText" in item["fields"]:
                body = item["fields"]["bodyText"]
            elif "fields" in item and "standfirst" in item["fields"]:
                body = item["fields"]["standfirst"]

            return dict(
                id=hashlib.sha1(link.encode()).hexdigest(),
                title=item["webTitle"],
                link=link,
                source="guardian",
                published=published,
                raw=body,
            )
        except Exception as e:
            logger.warning("Error converting Guardian item to row: %s", e)
            return None

    async def _bulk_insert(self, rows: list[dict]):
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
