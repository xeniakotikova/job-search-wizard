import logging

import httpx

from app.config import settings
from app.models import JobResult

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _format_message(job: JobResult) -> str:
    lines = [
        f"<b>{job.title}</b>",
        "",
        job.description,
        "",
        f"<a href=\"{job.link}\">Open vacancy</a>",
    ]
    if job.date:
        lines.insert(1, f"<i>{job.date}</i>")
    return "\n".join(lines)


async def send_job_to_telegram(job: JobResult) -> bool:
    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": _format_message(job),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Telegram API HTTP error: %s — %s", exc.response.status_code, exc.response.text)
            return False
        except httpx.RequestError as exc:
            logger.error("Telegram API request error: %s", exc)
            return False

    logger.info("Sent to Telegram: %s", job.title)
    return True


async def send_jobs_to_telegram(jobs: list[JobResult], limit: int = 7) -> int:
    """Send a list of job results to Telegram. Returns the count of successfully sent messages."""
    sent = 0
    for job in jobs[:limit]:
        if await send_job_to_telegram(job):
            sent += 1
    return sent
