import logging

import httpx

from app.config import settings
from app.models import JobResult

logger = logging.getLogger(__name__)

SERPAPI_URL = "https://serpapi.com/search"


async def search_jobs(query: str | None = None) -> list[JobResult]:
    """Search for job vacancies using SerpAPI Google engine."""
    params = {
        "api_key": settings.serpapi_api_key,
        "engine": "google",
        "q": query or settings.search_query,
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
    jobs = data.get("organic_results", [])

    results: list[JobResult] = []
    for job in jobs:
        results.append(
            JobResult(
                title=job.get("title", "No title"),
                description=job.get("snippet", "No description"),
                link=job.get("link", ""),
                date=job.get("date"),
            )
        )

    logger.info("Found %d job results for query: %s", len(results), query or settings.search_query)
    return results
