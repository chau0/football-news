import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from football_news.config_loader import load_json_cfg, load_html_cfg
from football_news.fetchers.guardian_fetcher import GuardianFetcher
from football_news.fetchers.newsapi_fetcher import NewsAPIFetcher
from football_news.fetchers.html_fetcher import HtmlListFetcher
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def build_tasks():
    tasks = []
    for cfg in load_json_cfg():
        if cfg["name"] == "guardian":
            tasks.append(GuardianFetcher(cfg).fetch())
        elif cfg["name"] == "newsapi":
            tasks.append(NewsAPIFetcher(cfg).fetch())

    for cfg in load_html_cfg():
        tasks.append(HtmlListFetcher(cfg).fetch())
    return tasks


async def run_once():
    counts = await asyncio.gather(*build_tasks())
    print("total new rows:", sum(counts))


def main():
    sched = AsyncIOScheduler()
    sched.add_job(lambda: asyncio.create_task(run_once()), "interval", minutes=5)
    sched.start()
    print("scheduler started (Ctrl-C to quit)")
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    asyncio.run(run_once())  # change to main() if you want the daemon
