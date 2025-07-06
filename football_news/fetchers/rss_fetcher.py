# football_news/fetchers/rss_fetcher.py
import hashlib
import asyncio
import datetime as dt
import feedparser
import httpx
from sqlalchemy.dialects.sqlite import insert  # NEW
from football_news.config import load_feeds
from football_news.storage.db import SessionLocal
from football_news.storage.models import Story
from football_news.utils.logger import logger


async def fetch_feed(feed):
    logger.info(f"Fetching feed: {feed.name} from {feed.url}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(feed.url)
            logger.debug(f"HTTP response status for {feed.name}: {r.status_code}")
    except httpx.TimeoutException:
        logger.error(f"Timeout while fetching feed: {feed.name}")
        return 0
    except Exception as e:
        logger.error(f"Error fetching feed {feed.name}: {e}")
        return 0

    try:
        parsed = feedparser.parse(r.content)
        logger.debug(f"Parsed {len(parsed.entries)} entries from {feed.name}")
    except Exception as e:
        logger.error(f"Error parsing feed {feed.name}: {e}")
        return 0

    # Build one list of dictionaries
    rows = []
    for e in parsed.entries:
        guid = hashlib.sha1(e.link.encode()).hexdigest()
        rows.append(
            dict(
                id=guid,
                title=e.title,
                link=e.link,
                source=feed.name,
                published=dt.datetime(
                    *getattr(e, "published_parsed", dt.datetime.utcnow().timetuple())[
                        :6
                    ],
                    tzinfo=dt.timezone.utc,
                ),
                raw=r.text,
            )
        )

    try:
        # Single INSERT … OR IGNORE handles all races + duplicates
        stmt = insert(Story).values(rows).prefix_with("OR IGNORE")  # 👈 key line
        session = SessionLocal()
        session.execute(stmt)
        session.commit()
        session.close()

        logger.info(f"Successfully processed {len(rows)} stories from {feed.name}")
        return len(rows)
    except Exception as e:
        logger.error(f"Database error while saving stories from {feed.name}: {e}")
        return 0


async def run_once():
    logger.info("Starting RSS fetch cycle")

    try:
        feeds = load_feeds()
        logger.info(f"Loaded {len(feeds)} feeds from configuration")
    except Exception as e:
        logger.error(f"Failed to load feeds configuration: {e}")
        return

    tasks = [fetch_feed(f) for f in feeds]
    try:
        counts = await asyncio.gather(*tasks)
        total_stories = sum(counts)
        logger.info(
            f"RSS fetch cycle completed. Total stories processed: {total_stories}"
        )
        print("Stories processed:", total_stories)
    except Exception as e:
        logger.error(f"Error during fetch cycle: {e}")
