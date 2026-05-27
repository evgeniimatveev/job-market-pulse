import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _parse_salary(listings: list[dict]) -> tuple[float | None, float | None, float | None, float]:
    """Extract salary stats from listings. Returns (avg, min, max, disclosed_pct)."""
    salaries = []
    for job in listings:
        sal_min = job.get("salary_min")
        sal_max = job.get("salary_max")
        if sal_min and sal_max and sal_min > 1000 and sal_max > 1000:
            salaries.append((sal_min + sal_max) / 2)

    if not listings:
        return None, None, None, 0.0

    disclosed_pct = round(len(salaries) / len(listings) * 100, 1)
    if not salaries:
        return None, None, None, disclosed_pct

    return round(sum(salaries) / len(salaries), 0), round(min(salaries), 0), round(max(salaries), 0), disclosed_pct


def _calc_remote_pct(listings: list[dict], location: str) -> float:
    """% of listings that appear remote-friendly."""
    if not listings:
        return 0.0
    if location.lower() == "remote":
        return 100.0
    remote_keywords = {"remote", "work from home", "wfh", "hybrid"}
    count = 0
    for job in listings:
        title = (job.get("title") or "").lower()
        desc = (job.get("description") or "").lower()[:500]
        if any(kw in title or kw in desc for kw in remote_keywords):
            count += 1
    return round(count / len(listings) * 100, 1)


def _normalize_demand(rows: list[dict]) -> list[dict]:
    """Add demand_score 0–100 normalized per run across all stacks (city-level)."""
    counts = [r["job_count"] for r in rows]
    min_c, max_c = min(counts), max(counts)
    for row in rows:
        if max_c == min_c:
            row["demand_score"] = 50.0
        else:
            row["demand_score"] = round((row["job_count"] - min_c) / (max_c - min_c) * 100, 1)
    return rows


def transform(raw_results: list[dict]) -> tuple[list[dict], dict]:
    """
    Transform raw API results into structured rows ready for DuckDB.
    Returns (history_rows, pipeline_run_meta).
    """
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    rows = []
    for r in raw_results:
        listings = r.get("listings", [])
        salary_avg, salary_min, salary_max, salary_pct = _parse_salary(listings)
        remote_pct = _calc_remote_pct(listings, r["location"])

        rows.append({
            "run_id": run_id,
            "fetched_at": r["fetched_at"],
            "tech_stack": r["tech_stack"],
            "location": r["location"],
            "job_count": r["job_count"],
            "demand_score": None,  # filled after normalization
            "salary_avg": salary_avg,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_disclosed_pct": salary_pct,
            "remote_pct": remote_pct,
        })

    rows = _normalize_demand(rows)

    finished_at = datetime.now(timezone.utc).isoformat()
    pipeline_meta = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": "success",
        "stacks_fetched": len(set(r["tech_stack"] for r in rows)),
        "total_api_calls": len(rows),
    }

    logger.info("Transform complete: %d rows, run_id=%s", len(rows), run_id)
    return rows, pipeline_meta
