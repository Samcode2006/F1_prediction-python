"""
backend/api.py
FastAPI server for the F1 Race Winner Prediction System.

Run with:
    python backend/run.py
    OR
    uvicorn backend.api:app --reload --port 8000

Endpoints:
    GET /api/predict             - top-3 + full ranked predictions (next race)
    GET /api/races               - all cached races
    GET /api/race/{year}/{round}/results  - historical race results
    GET /api/race/{year}/{round}/weather  - race weather summary
    GET /api/race/{year}/{round}/telemetry - lap summary per driver
    GET /api/constructors        - constructor standings from predictions
    GET /api/health              - health check
"""

import os
import sys

# Allow running from project root: `python backend/run.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from predictor import (
    TEAM_STRENGTH,
    calculate_constructor_standings,
    discover_races,
    get_score_breakdown,
    load_drivers,
    load_lap_summary,
    load_race_results_from_cache,
    load_weather_data,
    predict_winner,
)

# ── App Setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="F1 Race Winner Prediction API",
    description="Serves predictions, historical race data, weather and lap telemetry summaries.",
    version="2.0.0",
)

# Allow the Vite dev server (port 5173) and production build to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR   = "cache"
DRIVERS_CSV = "drivers.csv"


# ── Helper ─────────────────────────────────────────────────────────────────────

def _resolve_race(year: str, round_index: int) -> dict | None:
    """Find a race in the cache by year and 1-based round index."""
    races = discover_races(CACHE_DIR)
    year_races = [r for r in races if r["year"] == year]
    if round_index < 1 or round_index > len(year_races):
        return None
    return year_races[round_index - 1]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/predict")
def predict():
    """
    Returns ranked driver predictions for the next race based on drivers.csv.
    Response includes full breakdown and podium chance per driver.
    """
    if not os.path.isfile(DRIVERS_CSV):
        raise HTTPException(
            status_code=404,
            detail="drivers.csv not found. Run fetch_data.py first.",
        )

    drivers = load_drivers(DRIVERS_CSV)
    if not drivers:
        raise HTTPException(status_code=422, detail="drivers.csv is empty.")

    ranked = predict_winner(drivers)

    results = []
    for i, driver in enumerate(ranked, start=1):
        breakdown = get_score_breakdown(driver)
        results.append({
            "position":       i,
            "driver":         driver["Driver"],
            "team":           driver["Team"],
            "qualifying":     driver["Qualifying"],
            "previousFinish": driver["PreviousFinish"],
            "score":          driver["Score"],
            "teamStrength":   TEAM_STRENGTH.get(driver["Team"], 3),
            "teamColour":     _team_colour(driver["Team"]),
            "breakdown":      breakdown,
        })

    return {
        "podium": results[:3],
        "fullField": results,
        "totalDrivers": len(results),
    }


@app.get("/api/constructors")
def constructors():
    """Returns constructor standings derived from the current predictions."""
    if not os.path.isfile(DRIVERS_CSV):
        raise HTTPException(status_code=404, detail="drivers.csv not found.")

    drivers = load_drivers(DRIVERS_CSV)
    ranked  = predict_winner(drivers)
    standings = calculate_constructor_standings(ranked)
    return {"standings": standings}


@app.get("/api/races")
def races():
    """Returns all cached races grouped by year."""
    all_races = discover_races(CACHE_DIR)
    by_year: dict[str, list] = {}
    for r in all_races:
        by_year.setdefault(r["year"], []).append({
            "round":      by_year.get(r["year"], []).__len__() + 1,
            "trackName":  r["track_name"],
            "date":       r["date"],
            "folderName": r["folder_name"],
            "sessions":   r["sessions"],
        })
    return {"years": sorted(by_year.keys(), reverse=True), "races": by_year}


@app.get("/api/race/{year}/{round}/weather")
def race_weather(year: str, round: int):
    """Returns weather summary for a specific race."""
    race = _resolve_race(year, round)
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found.")

    weather = load_weather_data(CACHE_DIR, race["folder_name"])
    if weather is None:
        raise HTTPException(status_code=404, detail="Weather data not available for this race.")

    return {
        "year":      year,
        "round":     round,
        "trackName": race["track_name"],
        "weather":   weather,
    }


@app.get("/api/race/{year}/{round}/telemetry")
def race_telemetry(year: str, round: int):
    """Returns lap time summary (fastest lap, avg lap, tyre compounds) per driver."""
    race = _resolve_race(year, round)
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found.")

    laps = load_lap_summary(CACHE_DIR, race["folder_name"])
    driver_info = load_race_results_from_cache(CACHE_DIR, race["folder_name"])

    # Build a lookup by driver number for team colour / name
    info_by_num: dict[str, dict] = {}
    if driver_info:
        for d in driver_info:
            info_by_num[d["DriverNumber"]] = d

    enriched = []
    if laps:
        for lap in laps:
            info = info_by_num.get(lap["Driver"], {})
            enriched.append({
                **lap,
                "Abbreviation": info.get("Abbreviation", lap["Driver"]),
                "FullName":     info.get("FullName", ""),
                "TeamName":     info.get("TeamName", ""),
                "TeamColour":   "#" + info.get("TeamColour", "FFFFFF"),
            })

    return {
        "year":      year,
        "round":     round,
        "trackName": race["track_name"],
        "lapSummary": enriched,
    }


@app.get("/api/race/{year}/{round}/results")
def race_results(year: str, round: int):
    """Returns driver info (name, team, colour) for a race from the cache."""
    race = _resolve_race(year, round)
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found.")

    results = load_race_results_from_cache(CACHE_DIR, race["folder_name"])
    weather = load_weather_data(CACHE_DIR, race["folder_name"])

    if results is None:
        raise HTTPException(status_code=404, detail="Results not available for this race.")

    formatted = [
        {
            **r,
            "TeamColour": "#" + r.get("TeamColour", "FFFFFF"),
        }
        for r in results
    ]

    return {
        "year":      year,
        "round":     round,
        "trackName": race["track_name"],
        "date":      race["date"],
        "results":   formatted,
        "weather":   weather,
    }


# ── Utilities ──────────────────────────────────────────────────────────────────

_TEAM_COLOURS = {
    "Red Bull Racing":  "#3671C6",
    "McLaren":          "#FF8000",
    "Ferrari":          "#E8002D",
    "Mercedes":         "#27F4D2",
    "Aston Martin":     "#229971",
    "Alpine":           "#FF87BC",
    "Williams":         "#64C4FF",
    "Haas F1 Team":     "#B6BABD",
    "Racing Bulls":     "#6692FF",
    "Audi":             "#C92D4B",
    "Cadillac":         "#333399",
}


def _team_colour(team: str) -> str:
    return _TEAM_COLOURS.get(team, "#888888")
