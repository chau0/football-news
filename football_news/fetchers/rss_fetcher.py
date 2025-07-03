# football_news/fetchers/rss_fetcher.py
import hashlib
import asyncio
import feedparser
import httpx
import datetime as dt
from football_news.config import load_feeds
from football_news.storage.db import SessionLocal
from football_news.storage.models import Story


async def fetch_feed(feed):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(str(feed.url))
    parsed = feedparser.parse(r.content)
    session = SessionLocal()
    for e in parsed.entries:
        guid = hashlib.sha1(e.link.encode()).hexdigest()
        if not session.query(Story).filter_by(id=guid).first():
            story = Story(
                id=guid,
                title=e.title,
                link=e.link,
                source=feed.name,
                published=dt.datetime(*e.published_parsed[:6], tzinfo=dt.timezone.utc),
                raw=r.text,
            )
            session.add(story)
    session.commit()
    session.close()
    return len(parsed.entries)


async def run_once():
    tasks = [fetch_feed(f) for f in load_feeds()]
    counts = await asyncio.gather(*tasks)
    print("Inserted stories:", sum(counts))
