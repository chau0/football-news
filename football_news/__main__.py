# football_news/__main__.py
import asyncio
import typer
from football_news.fetchers.rss_fetcher import run_once
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from football_news.utils.logger import logger

app = typer.Typer()


@app.command()
def fetch():
    """Run single fetch cycle."""
    logger.info("Manual fetch command initiated")
    asyncio.run(run_once())


@app.command()
def daemon():
    """Run scheduler that triggers fetcher on interval."""
    logger.info("Starting daemon mode with 5-minute intervals")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(run_once()), "interval", minutes=5)
    scheduler.start()

    typer.echo("Scheduler started (Ctrl-C to exit)")
    logger.info("Scheduler started successfully")

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Daemon shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error in daemon mode: {e}")


if __name__ == "__main__":
    app()
