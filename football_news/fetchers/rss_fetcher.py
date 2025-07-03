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


async def fetch_feed(feed):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(feed.url)
    parsed = feedparser.parse(r.content)

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

    # Single INSERT … OR IGNORE handles all races + duplicates
    stmt = insert(Story).values(rows).prefix_with("OR IGNORE")  # 👈 key line
    session = SessionLocal()
    session.execute(stmt)
    session.commit()
    session.close()
    return len(rows)


async def run_once():
    tasks = [fetch_feed(f) for f in load_feeds()]
    counts = await asyncio.gather(*tasks)
    print("Stories processed:", sum(counts))
