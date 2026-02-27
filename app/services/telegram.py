import logging

import httpx

from app.config import settings
from app.models import JobResult

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"
TELEGRAM_API_URL = TELEGRAM_API_BASE + "/sendMessage"


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


async def send_message(chat_id: str | int, text: str) -> bool:
    """Send a plain-text message to a Telegram chat."""
    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("Failed to send message to Telegram: %s", exc)
            return False
    return True


async def setup_webhook(webhook_url: str) -> bool:
    """Register the webhook URL with Telegram."""
    url = (TELEGRAM_API_BASE + "/setWebhook").format(token=settings.telegram_bot_token)
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json={"url": webhook_url})
            response.raise_for_status()
            data = response.json()
            if data.get("result"):
                logger.info("Telegram webhook registered: %s", webhook_url)
                return True
            logger.error("Telegram setWebhook returned: %s", data)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("Failed to register Telegram webhook: %s", exc)
    return False


async def setup_bot_commands() -> bool:
    """Register /pause and /resume as bot menu commands in Telegram."""
    url = (TELEGRAM_API_BASE + "/setMyCommands").format(token=settings.telegram_bot_token)
    commands = [
        {"command": "pause", "description": "Pause the scheduled job search"},
        {"command": "resume", "description": "Resume the scheduled job search"},
    ]
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json={"commands": commands})
            response.raise_for_status()
            data = response.json()
            if data.get("result"):
                logger.info("Telegram bot commands registered")
                return True
            logger.error("Telegram setMyCommands returned: %s", data)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("Failed to register Telegram bot commands: %s", exc)
    return False
