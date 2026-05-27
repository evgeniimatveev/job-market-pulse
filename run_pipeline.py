import logging
import sys
from pathlib import Path

from src.extract import run_extraction
from src.transform import transform
from src.load import load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("pipeline")


def main():
    logger.info("=== Job Market Pulse pipeline starting ===")

    logger.info("Step 1/3: Extract")
    raw = run_extraction()

    logger.info("Step 2/3: Transform")
    history_rows, pipeline_meta = transform(raw)

    logger.info("Step 3/3: Load")
    db_path = Path("data/job_market.duckdb")
    load(history_rows, pipeline_meta, db_path)

    logger.info("=== Pipeline complete. run_id=%s ===", pipeline_meta["run_id"])


if __name__ == "__main__":
    main()
