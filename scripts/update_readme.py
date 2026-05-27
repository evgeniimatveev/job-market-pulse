"""
Auto-update README.md with latest market stats from DuckDB.
Runs after each pipeline execution — keeps the README as a live market report.
"""
import duckdb
import re
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/job_market.duckdb")
README_PATH = Path("README.md")
START_TAG = "<!-- MARKET_PULSE:START -->"
END_TAG   = "<!-- MARKET_PULSE:END -->"


def build_block(conn) -> str:
    # Latest run meta
    run = conn.execute(
        "SELECT run_id, finished_at, total_api_calls FROM pipeline_runs ORDER BY finished_at DESC LIMIT 1"
    ).fetchone()
    run_count = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
    total_records = conn.execute("SELECT COUNT(*) FROM job_market_history").fetchone()[0]

    finished_at = run[1]
    if hasattr(finished_at, "strftime"):
        date_str = finished_at.strftime("%b %d %Y")
    else:
        date_str = str(finished_at)[:10]

    latest_run_id = run[0]

    # Top stack by job count
    top = conn.execute("""
        SELECT tech_stack, SUM(job_count) as total
        FROM job_market_history WHERE run_id = ?
        GROUP BY tech_stack ORDER BY total DESC LIMIT 1
    """, [latest_run_id]).fetchone()

    # Highest paying
    pay = conn.execute("""
        SELECT tech_stack, ROUND(AVG(salary_avg), 0) as avg_sal
        FROM job_market_history
        WHERE run_id = ? AND salary_avg IS NOT NULL
        GROUP BY tech_stack ORDER BY avg_sal DESC LIMIT 1
    """, [latest_run_id]).fetchone()

    # Most remote
    remote = conn.execute("""
        SELECT tech_stack, ROUND(AVG(remote_pct), 1) as r
        FROM job_market_history
        WHERE run_id = ? AND location != 'remote'
        GROUP BY tech_stack ORDER BY r DESC LIMIT 1
    """, [latest_run_id]).fetchone()

    # Top 5 demand ranking
    ranking = conn.execute("""
        SELECT tech_stack,
               SUM(job_count) as jobs,
               ROUND(AVG(demand_score), 1) as score
        FROM job_market_history WHERE run_id = ?
        GROUP BY tech_stack ORDER BY jobs DESC LIMIT 5
    """, [latest_run_id]).fetchall()

    # Build markdown block
    lines = [
        START_TAG,
        "",
        f"## 📰 Today's Market Report",
        "",
        f"> 🗓️ **{date_str}** &nbsp;·&nbsp; Pipeline run **#{run_count}** &nbsp;·&nbsp; {total_records:,} total records",
        "",
        "| 🏆 Top Stack | 💰 Highest Paying | 🌐 Most Remote-Friendly |",
        "|---|---|---|",
        f"| **{top[0]}** — {top[1]:,} listings | **{pay[0]}** — ${int(pay[1]/1000)}k avg | **{remote[0]}** — {remote[1]:.0f}% remote |",
        "",
        "**Top 5 demand ranking (latest run):**",
        "",
        "| Rank | Stack | Listings | Demand Score |",
        "|------|-------|----------|--------------|",
    ]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (stack, jobs, score) in enumerate(ranking):
        lines.append(f"| {medals[i]} | **{stack}** | {jobs:,} | {score}/100 |")

    lines += [
        "",
        f"*Auto-updated daily by [GitHub Actions](.github/workflows/pipeline.yml) · Powered by [Adzuna API](https://www.adzuna.com/)*",
        "",
        END_TAG,
    ]
    return "\n".join(lines)


def update_readme(block: str) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_TAG) + r".*?" + re.escape(END_TAG),
        re.DOTALL,
    )
    if pattern.search(text):
        new_text = pattern.sub(block, text)
    else:
        # Insert before the first --- divider after the badges
        new_text = text.replace("\n---\n\nDaily tracking", f"\n{block}\n\n---\n\nDaily tracking", 1)
    README_PATH.write_text(new_text, encoding="utf-8")
    print("README updated with latest market stats.")


def main():
    if not DB_PATH.exists():
        print("No DB found — skipping README update.")
        return
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    block = build_block(conn)
    conn.close()
    update_readme(block)


if __name__ == "__main__":
    main()
