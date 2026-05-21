"""
Property-based tests for predictor.py functions.

Uses Hypothesis for property-based testing and pytest as the test runner.
"""

import sys
import os
import tempfile

# Ensure the project root is on the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from predictor import (
    calculate_podium_chance,
    calculate_constructor_standings,
    discover_tracks,
)

# load_weather_data will be available once task 1.4 is implemented
try:
    from predictor import load_weather_data
except ImportError:
    load_weather_data = None


# ──────────────────────────────────────────────
# Strategies for Property 6: Track name extraction
# ──────────────────────────────────────────────

# Strategy to generate valid date prefixes in YYYY-MM-DD format
date_prefix_strategy = st.builds(
    lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}",
    y=st.integers(min_value=2000, max_value=2099),
    m=st.integers(min_value=1, max_value=12),
    d=st.integers(min_value=1, max_value=28),
)

# Strategy to generate track name parts (words joined by underscores)
# Each word is at least 1 alphabetic character
track_word_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
    min_size=1,
    max_size=15,
)

track_name_strategy = st.lists(
    track_word_strategy,
    min_size=1,
    max_size=4,
).map(lambda words: "_".join(words))


# ──────────────────────────────────────────────
# Property 6: Track name extraction
# Feature: enhanced-prediction-ui, Property 6: Track name extraction
# ──────────────────────────────────────────────


@given(
    date_prefix=date_prefix_strategy,
    track_name_parts=track_name_strategy,
)
@settings(max_examples=100)
def test_property_6_track_name_extraction(date_prefix, track_name_parts):
    """
    Property 6: Track name extraction

    For any directory name matching the pattern YYYY-MM-DD_TrackName (where
    TrackName can contain underscores), the discover_tracks function shall
    extract the portion after the date prefix and replace all underscores
    with spaces.

    Feature: enhanced-prediction-ui, Property 6: Track name extraction
    **Validates: Requirements 4.1**
    """
    # Build the folder name: YYYY-MM-DD_TrackName
    folder_name = f"{date_prefix}_{track_name_parts}"

    # Expected track name: underscores replaced with spaces
    expected_track_name = track_name_parts.replace("_", " ")

    # Create a temporary directory structure mimicking the cache layout
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a year folder (use the year from the date prefix)
        year = date_prefix[:4]
        year_path = os.path.join(tmp_dir, year)
        os.makedirs(year_path)

        # Create the track folder inside the year folder
        track_path = os.path.join(year_path, folder_name)
        os.makedirs(track_path)

        # Call discover_tracks on the temp directory
        result = discover_tracks(tmp_dir)

        # Assert the returned track name has the date prefix removed
        # and underscores replaced with spaces
        assert expected_track_name in result, (
            f"Expected '{expected_track_name}' in result {result} "
            f"for folder '{folder_name}'"
        )


# ──────────────────────────────────────────────
# Feature: enhanced-prediction-ui
# Property 4: Constructor standings sort order
# ──────────────────────────────────────────────

# Strategy: generate a list of driver dicts with random Team and Score values
driver_dict_strategy = st.fixed_dictionaries({
    "Team": st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
        min_size=1,
        max_size=20,
    ),
    "Score": st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
})


@given(drivers=st.lists(driver_dict_strategy, min_size=1, max_size=30))
@settings(max_examples=100)
def test_constructor_standings_sort_order(drivers):
    """
    Property 4: Constructor standings sort order

    For any list of drivers with assigned scores, the output of
    calculate_constructor_standings SHALL be sorted in descending order
    by ConstructorScore, and when two teams have equal ConstructorScore,
    they SHALL be sorted alphabetically by team name.

    **Validates: Requirements 2.1**
    """
    standings = calculate_constructor_standings(drivers)

    # Assert sorted descending by ConstructorScore, ties broken alphabetically
    for i in range(len(standings) - 1):
        current = standings[i]
        next_item = standings[i + 1]

        # Primary sort: ConstructorScore descending
        assert current["ConstructorScore"] >= next_item["ConstructorScore"], (
            f"Standings not sorted descending by ConstructorScore: "
            f"{current['Team']} ({current['ConstructorScore']}) should be >= "
            f"{next_item['Team']} ({next_item['ConstructorScore']})"
        )

        # Secondary sort: alphabetical by team name when scores are equal
        if current["ConstructorScore"] == next_item["ConstructorScore"]:
            assert current["Team"] <= next_item["Team"], (
                f"Tied teams not sorted alphabetically: "
                f"'{current['Team']}' should come before '{next_item['Team']}' "
                f"(both have score {current['ConstructorScore']})"
            )

