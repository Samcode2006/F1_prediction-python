# predictor.py
# Core logic for the F1 Race Winner Prediction System
# Contains: load_drivers(), calculate_score(), predict_winner(), and helpers

import csv
import math
import os
import pickle

# ──────────────────────────────────────────────
# TEAM STRENGTH RATINGS (out of 10) — updated for 2026 grid
# Higher = stronger constructor
# ──────────────────────────────────────────────
TEAM_STRENGTH = {
    "Red Bull Racing":  10,
    "McLaren":           9,
    "Ferrari":           8,
    "Mercedes":          7,
    "Aston Martin":      5,
    "Alpine":            4,
    "Williams":          4,
    "Haas F1 Team":      3,
    "Racing Bulls":      3,   # was "RB" — updated to match FastF1 naming
    "Audi":              3,   # was "Kick Sauber" — rebranded for 2026
    "Cadillac":          2,   # new 2026 entry
}

# Tyre compound speed ranking (lower number = faster)
# Used for tyre-strategy bonus if tyre data is available
TYRE_SPEED_RANK = {
    "SOFT":   1,
    "MEDIUM": 2,
    "HARD":   3,
    "INTER":  4,
    "WET":    5,
}

# Championship points scale — used to model championship pressure momentum
# (top championship positions get a small confidence bonus)
CHAMPIONSHIP_PRESSURE_BONUS = {
    1: 3, 2: 2, 3: 2, 4: 1, 5: 1,
}


def load_drivers(filepath="drivers.csv"):
    """
    Reads driver data from a CSV file and returns a list of dictionaries.

    Each dictionary contains:
        - Driver        : driver name (string)
        - Team          : constructor name (string)
        - Qualifying    : grid position (integer, lower = better)
        - PreviousFinish: finish position in last race (integer, lower = better)

    Optional columns (used when present for enhanced scoring):
        - ChampPosition : championship standings position (integer)
        - GridPenalty   : grid position penalty applied (integer, 0 if none)
        - TyreCompound  : starting tyre compound (string, e.g. "SOFT")
        - Rainfall      : 1 if wet race expected, 0 if dry (integer)

    Parameters:
        filepath (str): path to the CSV file

    Returns:
        list of dict: one dictionary per driver

    Raises:
        FileNotFoundError: if the CSV file does not exist
    """
    drivers = []

    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                qual = int(row["Qualifying"])
                prev = int(row["PreviousFinish"])
            except (ValueError, KeyError) as e:
                print(f"  ⚠️  Skipping malformed row {dict(row)}: {e}")
                continue

            driver_data = {
                "Driver":          row["Driver"].strip(),
                "Team":            row["Team"].strip(),
                "Qualifying":      qual,
                "PreviousFinish":  prev,
                # Optional enhanced fields — default to neutral values
                "ChampPosition":   _safe_int(row.get("ChampPosition"), default=10),
                "GridPenalty":     _safe_int(row.get("GridPenalty"), default=0),
                "TyreCompound":    (row.get("TyreCompound") or "MEDIUM").strip().upper(),
                "Rainfall":        _safe_int(row.get("Rainfall"), default=0),
            }
            drivers.append(driver_data)

    return drivers


def _safe_int(value, default=0):
    """Convert a string to int, returning default on failure or if None/empty."""
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(str(value).strip())
    except ValueError:
        return default


def calculate_score(driver):
    """
    Calculates a prediction score for a single driver.
    Higher score = higher predicted chance of finishing well.

    Scoring rules:
        1. Qualifying bonus      : P1=10, P2=9, ..., P10=1, P11+=0 (capped at 0)
        2. Previous finish bonus : P1=10, P2=9, ..., P10=1, P11+=0
        3. Podium form bonus     : +5 pts if finished P1–P3 in previous race
        4. Team strength         : from TEAM_STRENGTH table (default 3 for unknown)
        5. Grid penalty          : -2 pts per grid penalty applied
        6. Tyre strategy bonus   : +2 if starting on SOFT, 0 on MEDIUM, -1 on HARD
        7. Wet race bonus        : +2 pts for teams with strong wet-weather history (TBC)
        8. Championship pressure : +1–3 pts for drivers in top-5 championship
        9. Qualifying trend      : small penalty if qualifying is worse than expected
           given team strength (prevents over-weighting a bad quali outlier)

    Parameters:
        driver (dict): a single driver dictionary from load_drivers()

    Returns:
        float: the driver's total prediction score
    """
    score = 0.0

    # Rule 1: Qualifying position (P1=10, P2=9, ..., P10=1, P11+ = capped at 0)
    qualifying_pos = driver["Qualifying"]
    qualifying_bonus = max(0, 11 - qualifying_pos)
    score += qualifying_bonus

    # Rule 2: Previous race finish bonus
    prev_finish = driver["PreviousFinish"]
    finish_bonus = max(0, 11 - prev_finish)
    score += finish_bonus

    # Rule 3: Podium form bonus
    if prev_finish <= 3:
        score += 5

    # Rule 4: Team strength
    team = driver["Team"]
    team_bonus = TEAM_STRENGTH.get(team, 3)
    score += team_bonus

    # Rule 5: Grid penalty deduction
    grid_penalty = driver.get("GridPenalty", 0)
    score -= grid_penalty * 2

    # Rule 6: Tyre compound bonus
    tyre = driver.get("TyreCompound", "MEDIUM").upper()
    tyre_bonus = {"SOFT": 2, "MEDIUM": 0, "HARD": -1, "INTER": 1, "WET": 1}.get(tyre, 0)
    score += tyre_bonus

    # Rule 7: Wet weather modifier — top teams perform better in the wet relative to midfield
    if driver.get("Rainfall", 0) == 1:
        wet_strength = max(0, team_bonus - 4)  # teams above "4" get a wet bonus
        score += wet_strength * 0.5

    # Rule 8: Championship pressure bonus for top-5 contenders
    champ_pos = driver.get("ChampPosition", 10)
    score += CHAMPIONSHIP_PRESSURE_BONUS.get(champ_pos, 0)

    return round(score, 2)


def get_score_breakdown(driver):
    """
    Returns a dictionary with the individual score contributions for a driver.
    Avoids duplicating the breakdown logic across main.py and app.py.

    Parameters:
        driver (dict): driver dict with 'Score' already computed

    Returns:
        dict: keys map each scoring rule to its point contribution
    """
    qual_pts      = max(0, 11 - driver["Qualifying"])
    finish_pts    = max(0, 11 - driver["PreviousFinish"])
    podium_pts    = 5 if driver["PreviousFinish"] <= 3 else 0
    team_pts      = TEAM_STRENGTH.get(driver["Team"], 3)
    penalty_pts   = -(driver.get("GridPenalty", 0) * 2)
    tyre          = driver.get("TyreCompound", "MEDIUM").upper()
    tyre_pts      = {"SOFT": 2, "MEDIUM": 0, "HARD": -1, "INTER": 1, "WET": 1}.get(tyre, 0)
    wet_pts       = 0
    if driver.get("Rainfall", 0) == 1:
        wet_pts = round(max(0, team_pts - 4) * 0.5, 2)
    champ_pts     = CHAMPIONSHIP_PRESSURE_BONUS.get(driver.get("ChampPosition", 10), 0)

    return {
        "Qualifying Bonus":    qual_pts,
        "Form Bonus":          finish_pts,
        "Podium Bonus":        podium_pts,
        "Team Strength":       team_pts,
        "Grid Penalty":        penalty_pts,
        "Tyre Bonus":          tyre_pts,
        "Wet Weather Bonus":   wet_pts,
        "Championship Bonus":  champ_pts,
        "Total":               driver.get("Score", calculate_score(driver)),
    }


def calculate_podium_chance(score: float, max_score: float = None) -> float:
    """
    Calculates the podium chance percentage for a driver based on their
    prediction score relative to the actual maximum possible score.

    Parameters:
        score (float): A driver's prediction score
        max_score (float): The maximum score in the current field (computed if None)

    Returns:
        float: Percentage chance rounded to 1 decimal place (0.0–100.0)
    """
    # Max possible score: qual(10) + finish(10) + podium(5) + team(10) + champ(3) + tyre(2) = 40
    _max = max_score if max_score is not None else 40.0
    if _max <= 0:
        return 0.0
    chance = round((score / _max) * 100, 1)
    return max(0.0, min(100.0, chance))


def predict_winner(drivers):
    """
    Calculates scores for all drivers and returns them sorted
    from highest score (predicted winner) to lowest.

    Parameters:
        drivers (list of dict): list of driver dictionaries from load_drivers()

    Returns:
        list of dict: drivers with a new 'Score' key, sorted descending
    """
    for driver in drivers:
        driver["Score"] = calculate_score(driver)

    ranked = sorted(drivers, key=lambda d: d["Score"], reverse=True)
    return ranked


def discover_tracks(cache_dir: str = "cache") -> list[str]:
    """
    Scans the cache folder structure to find available tracks.

    Returns:
        list[str]: alphabetically sorted list of unique track names
    """
    if not os.path.isdir(cache_dir):
        return []

    track_names = set()

    for year_folder in os.listdir(cache_dir):
        year_path = os.path.join(cache_dir, year_folder)
        if not os.path.isdir(year_path):
            continue

        for track_folder in os.listdir(year_path):
            track_path = os.path.join(year_path, track_folder)
            if not os.path.isdir(track_path):
                continue

            # Guard: folder must be longer than the YYYY-MM-DD_ prefix (11 chars)
            if len(track_folder) <= 11:
                continue

            raw_name = track_folder[11:]
            track_name = raw_name.replace("_", " ")
            if track_name:
                track_names.add(track_name)

    return sorted(track_names)


def discover_races(cache_dir: str = "cache") -> list[dict]:
    """
    Scans the cache folder and returns a structured list of all cached races.

    Returns:
        list[dict]: each dict has keys: year (str), track_name (str),
                    folder_name (str), date (str), sessions (list[str])
    """
    if not os.path.isdir(cache_dir):
        return []

    races = []

    for year_folder in sorted(os.listdir(cache_dir)):
        year_path = os.path.join(cache_dir, year_folder)
        if not os.path.isdir(year_path) or not year_folder.isdigit():
            continue

        for track_folder in sorted(os.listdir(year_path)):
            track_path = os.path.join(year_path, track_folder)
            if not os.path.isdir(track_path) or len(track_folder) <= 11:
                continue

            date_str = track_folder[:10]         # YYYY-MM-DD
            raw_name = track_folder[11:]
            track_name = raw_name.replace("_", " ")

            sessions = [
                s for s in os.listdir(track_path)
                if os.path.isdir(os.path.join(track_path, s))
            ]

            races.append({
                "year":        year_folder,
                "track_name":  track_name,
                "folder_name": track_folder,
                "date":        date_str,
                "sessions":    sessions,
            })

    return races


def get_track_folder_name(cache_dir: str, track_name: str) -> str | None:
    """
    Resolves a human-readable track name back to its cache folder name.
    Returns None if not found.
    """
    if not os.path.isdir(cache_dir):
        return None

    for year_folder in os.listdir(cache_dir):
        year_path = os.path.join(cache_dir, year_folder)
        if not os.path.isdir(year_path):
            continue
        for folder in os.listdir(year_path):
            folder_path = os.path.join(year_path, folder)
            if not os.path.isdir(folder_path) or len(folder) <= 11:
                continue
            if folder[11:].replace("_", " ") == track_name:
                return folder
    return None


def calculate_constructor_standings(ranked_drivers: list[dict]) -> list[dict]:
    """
    Aggregates driver scores by team and returns sorted constructor standings.

    Sorting:
        - Primary: ConstructorScore descending
        - Secondary (tie-breaker): team name alphabetically ascending

    Parameters:
        ranked_drivers (list of dict): driver dicts with 'Team' and 'Score' keys

    Returns:
        list of dict: constructor standings sorted by score descending
    """
    teams: dict[str, dict] = {}
    for driver in ranked_drivers:
        team_name = driver["Team"]
        if team_name not in teams:
            teams[team_name] = {"ConstructorScore": 0.0, "DriverCount": 0}
        teams[team_name]["ConstructorScore"] += driver["Score"]
        teams[team_name]["DriverCount"] += 1

    standings = []
    for team_name, data in teams.items():
        standings.append({
            "Team":             team_name,
            "ConstructorScore": data["ConstructorScore"],
            "TeamStrength":     TEAM_STRENGTH.get(team_name, 3),
            "DriverCount":      data["DriverCount"],
        })

    standings.sort(key=lambda x: (-x["ConstructorScore"], x["Team"]))
    return standings


def load_weather_data(cache_dir: str, track_folder_name: str) -> dict | None:
    """
    Loads weather data from a cached FastF1 Race session.

    Returns a dict with keys: air_temp, track_temp, rainfall, humidity, wind_speed
    or None if the data is unavailable.
    """
    try:
        track_path = None
        if os.path.isdir(cache_dir):
            for year_folder in os.listdir(cache_dir):
                year_path = os.path.join(cache_dir, year_folder)
                if not os.path.isdir(year_path):
                    continue
                candidate = os.path.join(year_path, track_folder_name)
                if os.path.isdir(candidate):
                    track_path = candidate
                    break

        if track_path is None:
            return None

        # Find the Race session subfolder (ends with _Race)
        race_folder = None
        for subfolder in os.listdir(track_path):
            subfolder_path = os.path.join(track_path, subfolder)
            if os.path.isdir(subfolder_path) and subfolder.endswith("_Race"):
                race_folder = subfolder_path
                break

        if race_folder is None:
            return None

        session_file = os.path.join(race_folder, "weather_data.ff1pkl")
        if not os.path.isfile(session_file):
            return None

        with open(session_file, "rb") as f:
            session_data = pickle.load(f)

        data = session_data.get("data", {})
        if not isinstance(data, dict):
            return None

        def get_avg(lst):
            if not lst:
                return "N/A"
            clean = [x for x in lst if x is not None and not math.isnan(x)]
            if not clean:
                return "N/A"
            return round(sum(clean) / len(clean), 1)

        return {
            "air_temp":   get_avg(data.get("AirTemp")),
            "track_temp": get_avg(data.get("TrackTemp")),
            "rainfall":   any(x == 1 for x in data.get("Rainfall", []) if x is not None),
            "humidity":   get_avg(data.get("Humidity")),
            "wind_speed": get_avg(data.get("WindSpeed")),
        }

    except Exception as e:
        print(f"Error loading weather data: {e}")
        return None


def load_lap_summary(cache_dir: str, track_folder_name: str) -> list[dict] | None:
    """
    Loads lap summary stats per driver from the cached FastF1 Race session.
    Reads the _extended_timing_data.ff1pkl file.

    Returns a list of dicts (one per driver), each with:
        - Driver        : 3-letter abbreviation
        - FastestLap    : fastest lap time as string (mm:ss.sss)
        - AvgLapTime    : average lap time in seconds
        - TopSpeed      : estimated from timing data if available
        - LapCount      : laps completed
        - TyreCompounds : list of compounds used
    or None if unavailable.
    """
    try:
        track_path = None
        if os.path.isdir(cache_dir):
            for year_folder in os.listdir(cache_dir):
                year_path = os.path.join(cache_dir, year_folder)
                if not os.path.isdir(year_path):
                    continue
                candidate = os.path.join(year_path, track_folder_name)
                if os.path.isdir(candidate):
                    track_path = candidate
                    break

        if track_path is None:
            return None

        race_folder = None
        for subfolder in os.listdir(track_path):
            subfolder_path = os.path.join(track_path, subfolder)
            if os.path.isdir(subfolder_path) and subfolder.endswith("_Race"):
                race_folder = subfolder_path
                break

        if race_folder is None:
            return None

        timing_file = os.path.join(race_folder, "_extended_timing_data.ff1pkl")
        if not os.path.isfile(timing_file):
            return None

        with open(timing_file, "rb") as f:
            timing_data = pickle.load(f)

        # The timing data is stored as {driver_num: {lap: {...}}}
        data = timing_data.get("data", {})
        if not isinstance(data, dict):
            return None

        summaries = []
        for driver_num, laps_dict in data.items():
            if not isinstance(laps_dict, dict):
                continue

            lap_times_sec = []
            compounds = []

            for lap_num, lap_data in laps_dict.items():
                if not isinstance(lap_data, dict):
                    continue

                # Extract lap time
                lt = lap_data.get("LapTime")
                if lt is not None:
                    try:
                        # LapTime may be a Timedelta or seconds float
                        secs = float(lt.total_seconds()) if hasattr(lt, "total_seconds") else float(lt)
                        if 60 < secs < 200:  # sanity check: valid F1 lap time
                            lap_times_sec.append(secs)
                    except (TypeError, ValueError):
                        pass

                # Extract compound
                compound = lap_data.get("Compound")
                if compound and compound not in compounds:
                    compounds.append(str(compound))

            if not lap_times_sec:
                continue

            fastest_sec = min(lap_times_sec)
            avg_sec = round(sum(lap_times_sec) / len(lap_times_sec), 3)

            def fmt_time(secs):
                mins = int(secs // 60)
                s = secs % 60
                return f"{mins}:{s:06.3f}"

            summaries.append({
                "Driver":        str(driver_num),
                "FastestLap":    fmt_time(fastest_sec),
                "FastestLapSec": round(fastest_sec, 3),
                "AvgLapTime":   avg_sec,
                "LapCount":     len(lap_times_sec),
                "TyreCompounds": compounds,
            })

        # Sort by fastest lap
        summaries.sort(key=lambda x: x["FastestLapSec"])
        return summaries if summaries else None

    except Exception as e:
        print(f"Error loading lap summary: {e}")
        return None


def load_race_results_from_cache(cache_dir: str, track_folder_name: str) -> list[dict] | None:
    """
    Loads race results from cached driver_info.ff1pkl in the Race session folder.

    Returns list of dicts with: DriverNumber, Abbreviation, FullName, TeamName,
    Position, ClassifiedPosition, GridPosition, Points, Status
    or None if unavailable.
    """
    try:
        track_path = None
        if os.path.isdir(cache_dir):
            for year_folder in os.listdir(cache_dir):
                year_path = os.path.join(cache_dir, year_folder)
                if not os.path.isdir(year_path):
                    continue
                candidate = os.path.join(year_path, track_folder_name)
                if os.path.isdir(candidate):
                    track_path = candidate
                    break

        if track_path is None:
            return None

        race_folder = None
        for subfolder in os.listdir(track_path):
            subfolder_path = os.path.join(track_path, subfolder)
            if os.path.isdir(subfolder_path) and subfolder.endswith("_Race"):
                race_folder = subfolder_path
                break

        if race_folder is None:
            return None

        driver_file = os.path.join(race_folder, "driver_info.ff1pkl")
        if not os.path.isfile(driver_file):
            return None

        with open(driver_file, "rb") as f:
            driver_data = pickle.load(f)

        data = driver_data.get("data", {})
        if not isinstance(data, dict):
            return None

        results = []
        for drv_num, info in data.items():
            if not isinstance(info, dict):
                continue
            results.append({
                "DriverNumber":       str(drv_num),
                "Abbreviation":       info.get("Abbreviation", ""),
                "FullName":           info.get("FullName", ""),
                "TeamName":           info.get("TeamName", ""),
                "TeamColour":         info.get("TeamColour", "FFFFFF"),
            })

        return results if results else None

    except Exception as e:
        print(f"Error loading race results from cache: {e}")
        return None
