"""Upload DuckDB file to Cloudflare R2 (same pattern as weather pipeline)."""
import os
import sys
from pathlib import Path

from r2_client import get_r2_client

BUCKET = os.environ["R2_BUCKET"]
KEY = "job-market-pulse/job_market.duckdb"
DB_PATH = Path("data/job_market.duckdb")


def main():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    get_r2_client().upload_file(str(DB_PATH), BUCKET, KEY)
    print(f"Uploaded {DB_PATH} to r2://{BUCKET}/{KEY}")


if __name__ == "__main__":
    main()
