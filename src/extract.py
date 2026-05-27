import os
import time
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs/us/search/1"
APP_ID = os.environ.get("ADZUNA_APP_ID", "ef196f72")
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "7f5419dff7d89699118f8e1c276f7d28")

TECH_STACKS = [
    "Python", "SQL", "Tableau", "Power BI", "dbt",
    "Spark", "Airflow", "Snowflake", "AWS", "Azure",
]

LOCATIONS = [
    "New York", "Los Angeles", "Chicago", "San Francisco", "Seattle",
    "Austin", "Boston", "Denver", "Atlanta", "Dallas", "remote",
]


def fetch_jobs(tech_stack: str, location: str, max_retries: int = 3) -> dict:
    """Fetch job listings for one tech_stack + location combo."""
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 50,
        "what": tech_stack,
        "content-type": "application/json",
    }
    if location.lower() == "remote":
        params["title_only"] = tech_stack
        params["what"] = f"{tech_stack} remote"
    else:
        params["where"] = location

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(ADZUNA_BASE, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {
                "tech_stack": tech_stack,
                "location": location,
                "job_count": data.get("count", 0),
                "listings": data.get("results", []),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        except requests.RequestException as e:
            logger.warning("Attempt %d failed for %s/%s: %s", attempt, tech_stack, location, e)
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    logger.error("All retries exhausted for %s/%s", tech_stack, location)
    return {
        "tech_stack": tech_stack,
        "location": location,
        "job_count": 0,
        "listings": [],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def run_extraction() -> list[dict]:
    """Fetch all 110 combinations. Returns list of raw result dicts."""
    results = []
    total = len(TECH_STACKS) * len(LOCATIONS)
    logger.info("Starting extraction: %d API calls", total)

    for i, stack in enumerate(TECH_STACKS):
        for j, loc in enumerate(LOCATIONS):
            call_num = i * len(LOCATIONS) + j + 1
            logger.info("[%d/%d] %s / %s", call_num, total, stack, loc)
            result = fetch_jobs(stack, loc)
            results.append(result)
            time.sleep(0.3)  # stay well under rate limits

    logger.info("Extraction complete: %d results", len(results))
    return results
