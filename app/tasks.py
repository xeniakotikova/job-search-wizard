import logging

from app.config import settings
from app.services.google_search import search_jobs
from app.services.telegram import send_jobs_to_telegram

logger = logging.getLogger(__name__)


async def job_search_task() -> None:
    """Search for fresh jobs and forward them to Telegram."""
    logger.info("Running job search for: %s", settings.search_query)
    jobs = await search_jobs()
    if not jobs:
        logger.info("No new job results found")
        return
    sent = await send_jobs_to_telegram(jobs)
    logger.info("Sent %d / %d results to Telegram", sent, len(jobs))
