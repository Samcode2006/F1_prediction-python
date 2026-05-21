# predictor.py
# Core logic for the F1 Race Winner Prediction System
# Contains: load_drivers(), calculate_score(), predict_winner()

import csv
import os
import pickle
import os

# ──────────────────────────────────────────────
# TEAM STRENGTH RATINGS (out of 10)
# Higher = stronger constructor
# ──────────────────────────────────────────────
TEAM_STRENGTH = {
    "Red Bull Racing": 10,
    "McLaren":        9,
    "Ferrari":        8,
    "Mercedes":       7,
    "Aston Martin":   5,
    "Alpine":         4,
    "Williams":       4,
    "Haas F1 Team":   3,
    "Kick Sauber":    3,
    "RB":             3,
}


def load_drivers(filepath="drivers.csv"):
    """
    Reads driver data from a CSV file and returns a list of dictionaries.

    Each dictionary contains:
        - Driver       : driver name (string)
        - Team         : constructor name (string)
        - Qualifying   : grid position (integer, lower = better)
        - PreviousFinish: finish position in last race (integer, lower = better)

    Parameters:
        filepath (str): path to the CSV file

    Returns:
        list of dict: one dictionary per driver
    """
    drivers = []

    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric columns from string to integer
            driver_data = {
                "Driver":         row["Driver"].strip(),
                "Team":           row["Team"].strip(),
                "Qualifying":     int(row["Qualifying"]),
                "PreviousFinish": int(row["PreviousFinish"]),
            }
            drivers.append(driver_data)

    return drivers


def calculate_score(driver):
    """
    Calculates a prediction score for a single driver.
    Higher score = higher chance of winning.

    Scoring rules:
        1. Qualifying bonus  : pole gets 10 pts, P2 gets 9 pts, etc. (max 10)
        2. Previous finish   : P1 last race gets 10 pts, P2 gets 9 pts, etc. (max 10)
        3. Podium bonus      : extra 5 pts if finished P1-P3 in previous race
        4. Team strength     : added directly from TEAM_STRENGTH table (max 10)

    Parameters:
        driver (dict): a single driver dictionary from load_drivers()

    Returns:
        float: the driver's total prediction score
    """
    score = 0

    # Rule 1: Qualifying position (pole = 10, P2 = 9, ...)
    qualifying_pos = driver["Qualifying"]
    qualifying_bonus = max(0, 11 - qualifying_pos)  # P1 → 10, P10 → 1
    score += qualifying_bonus

    # Rule 2: Previous race finish (P1 = 10, P2 = 9, ...)
    prev_finish = driver["PreviousFinish"]
    finish_bonus = max(0, 11 - prev_finish)          # P1 → 10, P10 → 1
    score += finish_bonus

    # Rule 3: Extra podium bonus for finishing in top 3 last race
    if prev_finish <= 3:
        score += 5  # podium form bonus

    # Rule 4: Team strength rating
    team = driver["Team"]
    team_bonus = TEAM_STRENGTH.get(team, 3)          # default 3 for unknown teams
    score += team_bonus

    return score


def calculate_podium_chance(score: float) -> float:
    """
    Calculates the podium chance percentage for a driver based on their
    prediction score.

    Formula: round((score / 35) * 100, 1), clamped between 0.0 and 100.0.

    Parameters:
        score (float): A driver's prediction score (typically 0–35)

    Returns:
        float: Percentage chance rounded to 1 decimal place (0.0–100.0)
    """
    chance = round((score / 35) * 100, 1)
    return max(0.0, min(100.0, chance))


def predict_winner(drivers):
    """
    Calculates scores for all drivers and returns them sorted
    from highest score (predicted winner) to lowest.

    Parameters:
        drivers (list of dict): list of driver dictionaries

    Returns:
        list of dict: drivers with a new 'Score' key, sorted descending
    """
    # Add a 'Score' field to each driver dictionary
    for driver in drivers:
        driver["Score"] = calculate_score(driver)

    # Sort by score, highest first
    ranked = sorted(drivers, key=lambda d: d["Score"], reverse=True)

    return ranked


def discover_tracks(cache_dir: str = "cache") -> list[str]:
    """
    Scans the cache folder structure to find available tracks.

    Iterates year folders in the cache directory, then subdirectories
    within each year. Extracts track names by removing the YYYY-MM-DD_
    date prefix (first 11 characters) and replacing underscores with spaces.

    Parameters:
        cache_dir (str): path to the cache directory (default: "cache")

    Returns:
        list[str]: alphabetically sorted list of unique track names,
                   or empty list if cache folder is missing or empty
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

            # Remove the YYYY-MM-DD_ prefix (first 11 characters)
            raw_name = track_folder[11:]
            # Replace underscores with spaces
            track_name = raw_name.replace("_", " ")
            track_names.add(track_name)

    return sorted(track_names)


def calculate_constructor_standings(ranked_drivers: list[dict]) -> list[dict]:
    """
    Aggregates driver scores by team and returns sorted constructor standings.

    For each team, computes:
        - ConstructorScore: sum of all driver Scores for that team
        - DriverCount: number of drivers belonging to that team
        - TeamStrength: rating from TEAM_STRENGTH dict (default 3 for unknown teams)

    Sorting:
        - Primary: ConstructorScore descending (highest first)
        - Secondary (tie-breaker): team name alphabetically ascending

    Parameters:
        ranked_drivers (list of dict): list of driver dicts, each with 'Team' and 'Score' keys

    Returns:
        list of dict: constructor standings sorted by score descending, ties alphabetical
    """
    # Aggregate scores and driver counts by team
    teams: dict[str, dict] = {}
    for driver in ranked_drivers:
        team_name = driver["Team"]
        if team_name not in teams:
            teams[team_name] = {"ConstructorScore": 0.0, "DriverCount": 0}
        teams[team_name]["ConstructorScore"] += driver["Score"]
        teams[team_name]["DriverCount"] += 1

    # Build the standings list
    standings = []
    for team_name, data in teams.items():
        standings.append({
            "Team": team_name,
            "ConstructorScore": data["ConstructorScore"],
            "TeamStrength": TEAM_STRENGTH.get(team_name, 3),
            "DriverCount": data["DriverCount"],
        })

    # Sort: descending by ConstructorScore, ties broken alphabetically by team name
    standings.sort(key=lambda x: (-x["ConstructorScore"], x["Team"]))

    return standings


def load_weather_data(cache_dir: str, track_folder_name: str) -> dict | None:
    """
    Loads weather data from a cached FastF1 Race session.
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

        # Load the weather_data.ff1pkl pickle file
        session_file = os.path.join(race_folder, "weather_data.ff1pkl")
        if not os.path.isfile(session_file):
            return None

        with open(session_file, "rb") as f:
            session_data = pickle.load(f)

        data = session_data.get("data", {})
        if not isinstance(data, dict):
            return None

        import math
        def get_avg(lst):
            if not lst: return "N/A"
            clean = [x for x in lst if x is not None and not math.isnan(x)]
            if not clean: return "N/A"
            return round(sum(clean) / len(clean), 1)

        return {
            'air_temp': get_avg(data.get("AirTemp")),
            'track_temp': get_avg(data.get("TrackTemp")),
            'rainfall': any([x == 1 for x in data.get("Rainfall") if x is not None]) if "Rainfall" in data else False,
            'humidity': get_avg(data.get("Humidity")),
            'wind_speed': get_avg(data.get("WindSpeed"))
        }

    except Exception as e:
        print(f"Error loading weather data: {e}")
        return None
