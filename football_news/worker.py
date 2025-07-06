"""
Enrichment daemon - fills summary + tags for new rows.
Run standalone or as a service.
"""

from __future__ import annotations
import asyncio
import logging
from itertools import islice

from football_news.storage.db import SessionLocal
from football_news.storage.models import Story
from processors.summary import summarise
from processors.tagger import tag

log = logging.getLogger("worker")
BATCH = 10  # LLM hits per wave
SLEEP = 60  # sec between idle polls


async def _enrich(rows):
    # summarise concurrently
    sums = await asyncio.gather(
        *[summarise(r.title, r.raw or "") for r in rows], return_exceptions=True
    )

    session = SessionLocal()
    for row, s in zip(rows, sums):
        if isinstance(s, Exception):
            log.error("summary failed %s: %s", row.id, s)
            continue
        row.summary = s
        row.tags = tag(f"{row.title}. {s}")
        session.add(row)
    session.commit()
    session.close()


async def main():
    while True:
        ses = SessionLocal()
        rows = ses.query(Story).filter(Story.summary.is_(None)).limit(100).all()
        ses.close()

        if not rows:
            await asyncio.sleep(SLEEP)
            continue

        it = iter(rows)
        tasks = []
        while chunk := list(islice(it, BATCH)):
            tasks.append(_enrich(chunk))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
