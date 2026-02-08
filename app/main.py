import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.models import JobResult
from app.scheduler import job_search_task, start_scheduler, stop_scheduler
from app.services.google_search import search_jobs
from app.services.telegram import send_jobs_to_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    logger.info("Application started")
    yield
    stop_scheduler()
    logger.info("Application stopped")


app = FastAPI(
    title="Job Search Bot",
    description="Searches for fresh job vacancies via Google and sends them to Telegram",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/search", response_model=list[JobResult])
async def search(q: str = Query(default=None, description="Custom search query")):
    """Run a one-off job search and return the results (does NOT send to Telegram)."""
    return await search_jobs(query=q)


@app.post("/search-and-send")
async def search_and_send(q: str = Query(default=None, description="Custom search query")):
    """Run a job search and send results to Telegram immediately."""
    jobs = await search_jobs(query=q)
    sent = await send_jobs_to_telegram(jobs)
    return {"found": len(jobs), "sent_to_telegram": sent}


@app.post("/trigger")
async def trigger():
    """Manually trigger the scheduled job search task."""
    await job_search_task()
    return {"status": "triggered"}
