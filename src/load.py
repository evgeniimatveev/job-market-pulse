import duckdb
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/job_market.duckdb")

DDL = """
CREATE TABLE IF NOT EXISTS job_market_history (
    run_id              VARCHAR,
    fetched_at          TIMESTAMPTZ,
    tech_stack          VARCHAR,
    location            VARCHAR,
    job_count           INTEGER,
    demand_score        DOUBLE,
    salary_avg          DOUBLE,
    salary_min          DOUBLE,
    salary_max          DOUBLE,
    salary_disclosed_pct DOUBLE,
    remote_pct          DOUBLE
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id          VARCHAR PRIMARY KEY,
    started_at      TIMESTAMPTZ,
    finished_at     TIMESTAMPTZ,
    status          VARCHAR,
    stacks_fetched  INTEGER,
    total_api_calls INTEGER
);
"""


def init_db(db_path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))
    conn.execute(DDL)
    return conn


def load(history_rows: list[dict], pipeline_meta: dict, db_path: Path = DB_PATH) -> None:
    conn = init_db(db_path)

    # Insert history rows
    conn.executemany(
        """
        INSERT INTO job_market_history VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        [
            (
                r["run_id"], r["fetched_at"], r["tech_stack"], r["location"],
                r["job_count"], r["demand_score"],
                r["salary_avg"], r["salary_min"], r["salary_max"],
                r["salary_disclosed_pct"], r["remote_pct"],
            )
            for r in history_rows
        ],
    )

    # Insert pipeline run log
    conn.execute(
        """
        INSERT OR REPLACE INTO pipeline_runs VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            pipeline_meta["run_id"],
            pipeline_meta["started_at"],
            pipeline_meta["finished_at"],
            pipeline_meta["status"],
            pipeline_meta["stacks_fetched"],
            pipeline_meta["total_api_calls"],
        ),
    )

    conn.close()
    logger.info("Loaded %d rows into %s", len(history_rows), db_path)
