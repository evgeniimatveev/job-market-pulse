"""Upload DuckDB file to HuggingFace Dataset (same pattern as weather pipeline)."""
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi

HF_REPO = os.environ.get("HF_REPO", "evgeniimatveev/job-market-pulse-db")
HF_TOKEN = os.environ["HF_TOKEN"]
DB_PATH = Path("data/job_market.duckdb")


def main():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    api = HfApi(token=HF_TOKEN)
    api.upload_file(
        path_or_fileobj=str(DB_PATH),
        path_in_repo="job_market.duckdb",
        repo_id=HF_REPO,
        repo_type="dataset",
    )
    print(f"Uploaded {DB_PATH} to {HF_REPO}")


if __name__ == "__main__":
    main()
