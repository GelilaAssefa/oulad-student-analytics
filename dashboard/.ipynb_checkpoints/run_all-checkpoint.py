"""
run_all.py
Master script — loads data into SQLite, runs all analysis, generates all charts.
Run from project root: python run_all.py
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    log.info("=" * 60)
    log.info("  OULAD Student Analytics — Full Pipeline")
    log.info("=" * 60)

    log.info("\n[1/2] Loading CSV data into SQLite database...")
    from src.utils.load_data import load_all
    load_all()

    log.info("\n[2/2] Running EDA and generating charts...")
    from src.analysis.eda import run_eda
    run_eda()

    log.info("\n" + "=" * 60)
    log.info("  Done! Charts saved to docs/reports/")
    log.info("  Launch dashboard: python dashboard/app.py")
    log.info("  Then open: http://localhost:8050")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
