"""
bulk_fetch.py
Pre-populates the FastF1 cache for 2024, 2025, and 2026 seasons.
Run this once (or when new races finish) before using app.py or build_dataset.py.

Usage:
    python bulk_fetch.py
    python bulk_fetch.py --years 2025 2026
"""

import argparse
import datetime
import logging
import os
import sys

import fastf1
import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
CACHE_DIR = "cache"
LOG_FILE  = "bulk_fetch_errors.log"
DEFAULT_YEARS = [2024, 2025, 2026]

os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def fetch_year(year: int):
    """Fetch all past races for a given season."""
    log.info("=" * 60)
    log.info(f"  Season {year}")
    log.info("=" * 60)

    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        log.error(f"Could not fetch schedule for {year}: {e}")
        return

    now = pd.Timestamp(datetime.datetime.now())
    past_races = schedule[
        (schedule["EventDate"] < now) & (schedule["RoundNumber"] > 0)
    ]

    if past_races.empty:
        log.info(f"  No past races found for {year}.")
        return

    for _, race in past_races.iterrows():
        race_name = race["EventName"]
        log.info(f"  Fetching: {year} — {race_name}")

        for session_type in ("Q", "R"):
            label = "Qualifying" if session_type == "Q" else "Race"
            try:
                session = fastf1.get_session(year, race_name, session_type)
                # telemetry=False keeps files small; weather=True needed for UI
                session.load(telemetry=False, weather=True, messages=False)
                log.info(f"    ✅ {label} loaded")
            except Exception as e:
                log.error(f"    ❌ {label} FAILED for {year} {race_name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Pre-populate the FastF1 cache for one or more seasons."
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=DEFAULT_YEARS,
        help=f"Seasons to fetch (default: {DEFAULT_YEARS})",
    )
    args = parser.parse_args()

    log.info(f"Starting bulk fetch for years: {args.years}")
    for year in args.years:
        fetch_year(year)
    log.info("Bulk fetch complete. Errors (if any) saved to: " + LOG_FILE)


if __name__ == "__main__":
    main()
