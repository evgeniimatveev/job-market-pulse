"""Download DuckDB file from HuggingFace Dataset before pipeline run."""
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

HF_REPO = os.environ.get("HF_REPO", "evgeniimatveev/job-market-pulse-db")
HF_TOKEN = os.environ.get("HF_TOKEN")
DB_PATH = Path("data/job_market.duckdb")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        path = hf_hub_download(
            repo_id=HF_REPO,
            filename="job_market.duckdb",
            repo_type="dataset",
            token=HF_TOKEN,
            local_dir="data",
            local_dir_use_symlinks=False,
        )
        print(f"Downloaded DB → {path}")
    except Exception as e:
        print(f"No existing DB found (first run?): {e}")
        print("Starting with fresh database.")


if __name__ == "__main__":
    main()
