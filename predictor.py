# predictor.py
# Core logic for the F1 Race Winner Prediction System
# Contains: load_drivers(), calculate_score(), predict_winner()

import csv

# ──────────────────────────────────────────────
# TEAM STRENGTH RATINGS (out of 10)
# Higher = stronger constructor
# ──────────────────────────────────────────────
TEAM_STRENGTH = {
    "Red Bull":      10,
    "McLaren":        9,
    "Ferrari":        8,
    "Mercedes":       7,
    "Aston Martin":   5,
    "Alpine":         4,
    "Williams":       4,
    "Haas":           3,
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
