import logging

import httpx

from app.config import settings
from app.models import JobResult

logger = logging.getLogger(__name__)

SERPAPI_URL = "https://serpapi.com/search"


async def search_jobs(query: str | None = None) -> list[JobResult]:
    """Search for job vacancies using SerpAPI Google Jobs engine.

    Uses the `chips=date_posted:today` parameter to restrict results to
    today's postings so only fresh listings appear.
    """
    params = {
        "api_key": settings.serpapi_api_key,
        "engine": "google_jobs",
        "q": query or settings.search_query,
        "chips": "date_posted:today",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(SERPAPI_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("SerpAPI HTTP error: %s — %s", exc.response.status_code, exc.response.text)
            return []
        except httpx.RequestError as exc:
            logger.error("SerpAPI request error: %s", exc)
            return []

    data = response.json()
    jobs = data.get("jobs_results", [])

    results: list[JobResult] = []
    for job in jobs:
        apply_options = job.get("apply_options", [])
        link = apply_options[0].get("link", "") if apply_options else ""

        detected = job.get("detected_extensions", {})
        date = detected.get("posted_at")

        results.append(
            JobResult(
                title=job.get("title", "No title"),
                description=job.get("description", "No description"),
                link=link,
                date=date,
            )
        )

    logger.info("Found %d job results for query: %s", len(results), query or settings.search_query)
    return results
