"""Download DuckDB file from Cloudflare R2 before pipeline run / dashboard start."""
from pathlib import Path

from botocore.exceptions import ClientError
from r2_client import get_r2_client
import os

BUCKET = os.environ["R2_BUCKET"]
KEY = "job-market-pulse/job_market.duckdb"
DB_PATH = Path("data/job_market.duckdb")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        get_r2_client().download_file(BUCKET, KEY, str(DB_PATH))
        print(f"Downloaded DB -> {DB_PATH}")
    except ClientError as e:
        print(f"No existing DB found (first run?): {e}")
        print("Starting with fresh database.")


if __name__ == "__main__":
    main()
