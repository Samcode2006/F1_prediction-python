# fetch_data.py
# Fetches real F1 data using FastF1 and writes it to drivers.csv
# Usage: python fetch_data.py
# Run this before main.py or app.py to refresh the data

import fastf1
import pandas as pd

# ── CONFIG — change these to fetch different races ──
SEASON       = 2025
QUALI_RACE   = 'Australia' # First race of 2025 season
PREV_RACE    = 'Australia' # race to get previous finish from
                            # (set to a different round for more realistic data)
CACHE_DIR    = 'cache'     # FastF1 caches data here to avoid re-downloading
OUTPUT_CSV   = 'drivers.csv'

# Enable caching — highly recommended, avoids hammering the API
# Enable caching — create the folder first if it doesn't exist
import os
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

def fetch_qualifying_positions(season, race):
    """
    Returns a dict: { driver_full_name: grid_position }
    Uses the Qualifying session results.
    """
    print(f"  Fetching qualifying data: {season} {race}...")
    session = fastf1.get_session(season, race, 'Q')
    session.load(telemetry=False, weather=False, messages=False)

    positions = {}
    for _, row in session.results.iterrows():
        name = row['FullName']
        # Some drivers may have NaN if they didn't set a qualifying time
        if pd.isna(row['Position']):
            continue  # skip this driver
        pos  = int(row['Position'])
        positions[name] = pos
    return positions

def fetch_race_results(season, race):
    """
    Returns a dict: { driver_full_name: finish_position }
    Uses the Race session results.
    """
    print(f"  Fetching race result data: {season} {race}...")
    session = fastf1.get_session(season, race, 'R')
    session.load(telemetry=False, weather=False, messages=False)

    results = {}
    teams   = {}
    for _, row in session.results.iterrows():
        name             = row['FullName']
        results[name]    = int(row['ClassifiedPosition']) if str(row['ClassifiedPosition']).isdigit() else 20
        teams[name]      = row['TeamName']

    return results, teams


def build_csv(quali_positions, race_results, teams):
    """
    Merges qualifying and race data into a DataFrame
    and writes it to drivers.csv in the correct format.
    """
    rows = []

    for name, grid_pos in quali_positions.items():
        # Use last name only to match your existing CSV style
        last_name     = name.split()[-1]
        team          = teams.get(name, "Unknown")
        prev_finish   = race_results.get(name, 20)  # default 20 if not found

        rows.append({
            "Driver":        last_name,
            "Team":          team,
            "Qualifying":    grid_pos,
            "PreviousFinish": prev_finish,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n  ✅ Saved {len(df)} drivers to {OUTPUT_CSV}")
    print(df.to_string(index=False))


def main():
    print("=" * 50)
    print("  F1 Data Fetcher — powered by FastF1")
    print("=" * 50)

    quali   = fetch_qualifying_positions(SEASON, QUALI_RACE)
    results, teams = fetch_race_results(SEASON, PREV_RACE)
    build_csv(quali, results, teams)

    print("\n  Run main.py or app.py to see predictions.")
    print("=" * 50)


if __name__ == "__main__":
    main()