from __future__ import annotations

import asyncio
import hashlib
import datetime as dt
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy.dialects.sqlite import insert

from football_news.fetchers.base import BaseFetcher
from football_news.middlewares.ratelimit import with_rate_limit
from football_news.storage.db import SessionLocal
from football_news.storage.models import Story


class HtmlListFetcher(BaseFetcher):
    """Scrapes a *list page* (no JS) using selectors from html.yml."""

    @with_rate_limit
    async def _call(self):
        hdrs = {"User-Agent": "football-news-bot/0.2 (+https://example.com)"}
        return await self._get(self.cfg["url"], headers=hdrs)

    async def fetch(self) -> int:
        html = (await self._call()).text
        soup = BeautifulSoup(html, "lxml")

        rows = []
        for item in soup.select(self.cfg["list_selector"]):
            href = item.select_one(self.cfg["link_selector"]).get("href")
            link = urljoin(self.cfg["url"], href)
            rows.append(
                dict(
                    id=hashlib.sha1(link.encode()).hexdigest(),
                    title=item.select_one(self.cfg["title_selector"]).get_text(
                        strip=True
                    ),
                    link=link,
                    source=self.cfg["name"],
                    published=self._parse_date(item),
                    raw=None,
                )
            )

        await self._bulk_insert(rows)
        return len(rows)

    def _parse_date(self, item):
        sel = self.cfg.get("date_selector")
        if not sel:
            return dt.datetime.utcnow()
        node = item.select_one(sel)
        if not node:
            return dt.datetime.utcnow()
        txt = node.get("datetime") or node.get_text(strip=True)
        try:
            return dt.datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except ValueError:
            # fallback – many sites use "03 Jul 2025"
            return dt.datetime.strptime(txt, "%d %b %Y")

    async def _bulk_insert(self, rows):
        if not rows:
            return
        stmt = insert(Story).values(rows).prefix_with("OR IGNORE")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._commit, stmt)

    @staticmethod
    def _commit(stmt):
        s = SessionLocal()
        s.execute(stmt)
        s.commit()
        s.close()
