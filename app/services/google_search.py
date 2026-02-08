import logging

import httpx

from app.config import settings
from app.models import JobResult

logger = logging.getLogger(__name__)

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


async def search_jobs(query: str | None = None) -> list[JobResult]:
    """Search for job vacancies using Google Custom Search API.

    Uses the `dateRestrict` parameter set to `d0` (past day — the smallest
    granularity the API offers).  The `sort=date` parameter ensures results
    are ordered newest-first so the freshest postings appear at the top.
    """
    params = {
        "key": settings.google_api_key,
        "cx": settings.google_cse_id,
        "q": query or settings.search_query,
        "dateRestrict": "d0",
        "sort": "date",
        "num": 10,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(GOOGLE_SEARCH_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Google API HTTP error: %s — %s", exc.response.status_code, exc.response.text)
            return []
        except httpx.RequestError as exc:
            logger.error("Google API request error: %s", exc)
            return []

    data = response.json()
    items = data.get("items", [])

    results: list[JobResult] = []
    for item in items:
        metatags = {}
        if pagemap := item.get("pagemap"):
            for tag in pagemap.get("metatags", []):
                metatags.update(tag)

        date = (
            item.get("snippet", "").split(" ... ")[0]
            if " ... " in item.get("snippet", "")
            else metatags.get("article:published_time", metatags.get("og:updated_time"))
        )

        results.append(
            JobResult(
                title=item.get("title", "No title"),
                description=item.get("snippet", "No description"),
                link=item.get("link", ""),
                date=date,
            )
        )

    logger.info("Found %d job results for query: %s", len(results), query or settings.search_query)
    return results
