# football_news/__main__.py
import asyncio
import typer
from football_news.fetchers.rss_fetcher import run_once
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = typer.Typer()


@app.command()
def fetch():
    """Run single fetch cycle."""
    asyncio.run(run_once())


@app.command()
def daemon():
    """Run scheduler that triggers fetcher on interval."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(run_once()), "interval", minutes=5)
    scheduler.start()
    typer.echo("Scheduler started (Ctrl-C to exit)")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    app()
