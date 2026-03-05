import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Query, Request

from app.config import settings
from app.models import JobResult
from app.tasks import job_search_task
from app.services.google_search import search_jobs
from app.services.telegram import send_jobs_to_telegram, send_message, setup_bot_commands, setup_webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.webhook_url:
        await setup_webhook(settings.webhook_url)
        await setup_bot_commands()
    logger.info("Application started")
    yield


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
    """Manually trigger the job search task."""
    await job_search_task()
    return {"status": "triggered"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates."""
    data = await request.json()

    message = data.get("message") or data.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "")

    if chat_id != str(settings.telegram_chat_id):
        return {"ok": True}

    if text.startswith("/search"):
        await send_message(chat_id, "Starting job search...")
        await job_search_task()

    return {"ok": True}
