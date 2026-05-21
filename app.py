# app.py
# Streamlit web app for the F1 Race Winner Prediction System
# Run with: streamlit run app.py

import streamlit as st
import pandas as pd
import os
from predictor import load_drivers, predict_winner, TEAM_STRENGTH, discover_tracks, load_weather_data, calculate_podium_chance, calculate_constructor_standings

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="F1 Race Winner Predictor",
    page_icon="🏎️",
    layout="wide"
)

# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────

def get_drivers():
    """Load raw driver data from CSV. Returns empty list on failure."""
    try:
        # Load fresh if the file changes; typically caching would need to watch the file
        return load_drivers("drivers.csv")
    except FileNotFoundError:
        return None  # Handle error outside the cached function

base_drivers = get_drivers()

if base_drivers is None:
    st.error("❌ `drivers.csv` not found. Make sure it's in the same folder as `app.py`.")
    st.stop()  # Halt the app cleanly — nothing below runs

if len(base_drivers) == 0:
    st.error("❌ `drivers.csv` is empty — no driver records found.")
    st.stop()

# Calculate predictions with actual values
ranked_drivers = predict_winner(base_drivers)

# ──────────────────────────────────────────────
# SIDEBAR — Driver Selector
# ──────────────────────────────────────────────

# Build driver name list in CSV file order (base_drivers order)
driver_names = [d["Driver"] for d in base_drivers]

selected_driver_name = st.sidebar.selectbox(
    "Select Driver",
    options=driver_names,
    help="Choose a driver to view their prediction details"
)

# Find the selected driver's data from ranked_drivers (which has Score)
selected_driver = next(d for d in ranked_drivers if d["Driver"] == selected_driver_name)

# Display selected driver's details
st.sidebar.markdown(f"**Team:** {selected_driver['Team']}")
st.sidebar.markdown(f"**Qualifying Position:** P{selected_driver['Qualifying']}")
st.sidebar.markdown(f"**Previous Finish:** P{selected_driver['PreviousFinish']}")
st.sidebar.markdown(f"**Prediction Score:** {selected_driver['Score']}")

# Predict Podium Chance button
if st.sidebar.button("Predict Podium Chance"):
    podium_chance = calculate_podium_chance(selected_driver["Score"])
    if podium_chance > 70:
        st.sidebar.success(f"🏆 Podium Chance: {podium_chance}%")
    elif podium_chance >= 40:
        st.sidebar.warning(f"⚠️ Podium Chance: {podium_chance}%")
    else:
        st.sidebar.info(f"ℹ️ Podium Chance: {podium_chance}%")

st.sidebar.divider()

# ──────────────────────────────────────────────
# SIDEBAR — Track Selector with error handling
# ──────────────────────────────────────────────

available_tracks = discover_tracks("cache")

if available_tracks:
    selected_tracks = st.sidebar.multiselect(
        "Select Tracks",
        options=available_tracks,
        help="Choose one or more tracks to view weather data"
    )
    if not selected_tracks:
        st.sidebar.info("Select at least one track to view weather information.")
else:
    selected_tracks = []
    st.sidebar.info("ℹ️ No tracks available. Cache folder is empty or missing.")

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────

st.title("🏎️ F1 Race Winner Prediction System 🏁")
st.caption("Rule-based prediction using qualifying position, recent form, and team strength.")
st.divider()

# ──────────────────────────────────────────────
# WINNER SECTION — st.metric looks much cleaner than success/info/warning
# ──────────────────────────────────────────────

st.subheader("🏆 Predicted Race Winner")

winner  = ranked_drivers[0]
second  = ranked_drivers[1]
third   = ranked_drivers[2]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🥇 Winner",
        value=winner["Driver"],
        delta=f"{winner['Team']} · {winner['Score']} pts"
    )
with col2:
    st.metric(
        label="🥈 2nd Place",
        value=second["Driver"],
        delta=f"{second['Team']} · {second['Score']} pts"
    )
with col3:
    st.metric(
        label="🥉 3rd Place",
        value=third["Driver"],
        delta=f"{third['Team']} · {third['Score']} pts"
    )

st.divider()

# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Full Rankings", "📊 Score Breakdown", "📈 Score Chart", "🏗️ Constructor Standings", "🌤️ Weather Info"])

# ── TAB 1: Rankings table ──────────────────────
with tab1:
    st.subheader("Full Driver Rankings")

    display_data = []
    for i, driver in enumerate(ranked_drivers, 1):
        if i == 1:   pos = "🥇 1st"
        elif i == 2: pos = "🥈 2nd"
        elif i == 3: pos = "🥉 3rd"
        else:        pos = f"P{i}"

        display_data.append({
            "Position":       pos,
            "Driver":         driver["Driver"],
            "Team":           driver["Team"],
            "Qualifying":     driver["Qualifying"],
            "Previous Finish":driver["PreviousFinish"],
            "Score":          driver["Score"],
        })

    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── TAB 2: Score breakdown table ──────────────
with tab2:
    st.subheader("Score Breakdown per Driver")
    st.caption("Shows exactly how each driver's total score was calculated.")

    breakdown_data = []
    for driver in ranked_drivers:
        qual_pts   = max(0, 11 - driver["Qualifying"])
        finish_pts = max(0, 11 - driver["PreviousFinish"])
        podium_pts = 5 if driver["PreviousFinish"] <= 3 else 0
        team_pts   = TEAM_STRENGTH.get(driver["Team"], 3)

        breakdown_data.append({
            "Driver":           driver["Driver"],
            "Team":             driver["Team"],
            "Qualifying Bonus": qual_pts,
            "Form Bonus":       finish_pts,
            "Podium Bonus":     podium_pts,
            "Team Strength":    team_pts,
            "Total Score":      driver["Score"],
        })

    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

# ── TAB 3: Bar chart ──────────────────────────
with tab3:
    st.subheader("Predicted Scores — Visual Comparison")
    st.caption("Higher score = more likely to win.")

    # Build a DataFrame indexed by driver name for the chart
    chart_df = pd.DataFrame({
        "Driver": [d["Driver"] for d in ranked_drivers],
        "Score":  [d["Score"]  for d in ranked_drivers],
    }).set_index("Driver")

    st.bar_chart(chart_df, use_container_width=True)

# ── TAB 4: Constructor Standings ───────────────
with tab4:
    st.subheader("🏗️ Constructor Standings")

    constructor_standings = calculate_constructor_standings(ranked_drivers)
    constructor_df = pd.DataFrame(constructor_standings)
    st.dataframe(constructor_df[["Team", "ConstructorScore", "TeamStrength", "DriverCount"]], use_container_width=True, hide_index=True)

# ── TAB 5: Weather Info ───────────────────────
with tab5:
    st.subheader("🌤️ Weather Information")

    if not selected_tracks:
        st.info("Select one or more tracks from the sidebar to view weather information.")
    else:
        for track_name in selected_tracks:
            # Convert human-readable track name back to folder format for lookup
            track_folder_name = None
            # Search cache for matching track folder
            cache_dir = "cache"
            if os.path.isdir(cache_dir):
                for year_folder in os.listdir(cache_dir):
                    year_path = os.path.join(cache_dir, year_folder)
                    if not os.path.isdir(year_path):
                        continue
                    for folder in os.listdir(year_path):
                        folder_path = os.path.join(year_path, folder)
                        if not os.path.isdir(folder_path):
                            continue
                        # Check if this folder matches the track name
                        raw_name = folder[11:]  # Remove YYYY-MM-DD_ prefix
                        if raw_name.replace("_", " ") == track_name:
                            track_folder_name = folder
                            break
                    if track_folder_name:
                        break

            with st.container():
                st.markdown(f"**{track_name}**")
                if track_folder_name:
                    weather = load_weather_data(cache_dir, track_folder_name)
                    if weather:
                        st.text(f"🌡️ Air Temperature: {weather['air_temp']}°C")
                        st.text(f"🛤️ Track Temperature: {weather['track_temp']}°C")
                        st.text(f"🌧️ Rainfall: {'Wet' if weather['rainfall'] else 'Dry'}")
                        if "humidity" in weather:
                            st.text(f"💧 Humidity: {weather['humidity']}%")
                        if "wind_speed" in weather:
                            st.text(f"💨 Wind Speed: {weather['wind_speed']} km/h")
                    else:
                        st.info(f"Weather information is not available for {track_name}.")
                else:
                    st.info(f"Weather information is not available for {track_name}.")
                st.divider()