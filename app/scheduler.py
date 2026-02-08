import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.google_search import search_jobs
from app.services.telegram import send_jobs_to_telegram

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def job_search_task() -> None:
    """Periodic task: search for fresh jobs and forward them to Telegram."""
    logger.info("Running scheduled job search for: %s", settings.search_query)
    jobs = await search_jobs()
    if not jobs:
        logger.info("No new job results found")
        return
    sent = await send_jobs_to_telegram(jobs)
    logger.info("Sent %d / %d results to Telegram", sent, len(jobs))


def _run_task() -> None:
    """Wrapper so APScheduler can fire the coroutine from its thread."""
    asyncio.get_event_loop().create_task(job_search_task())


def start_scheduler() -> None:
    scheduler.add_job(
        _run_task,
        "interval",
        minutes=settings.search_interval_minutes,
        id="job_search",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — job search runs every %d minutes",
        settings.search_interval_minutes,
    )


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
