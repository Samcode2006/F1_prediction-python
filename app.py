# app.py
# Streamlit web app for the F1 Race Winner Prediction System
# Run with: streamlit run app.py

import streamlit as st
import pandas as pd
from predictor import load_drivers, predict_winner, TEAM_STRENGTH

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="F1 Race Winner Predictor",
    page_icon="🏎️",
    layout="wide"
)

# ──────────────────────────────────────────────
# LOAD DATA (cached so it doesn't reload on every interaction)
# ──────────────────────────────────────────────

def get_drivers():
    """Load raw driver data from CSV. Returns empty list on failure."""
    try:
        # Load fresh if the file changes; typically caching would need to watch the file
        return load_drivers("drivers.csv")
    except FileNotFoundError:
        return None  # Handle error outside the cached function


# ──────────────────────────────────────────────
# SIDEBAR — Live input editor
# ──────────────────────────────────────────────

st.sidebar.title("⚙️ Adjust Inputs")
st.sidebar.markdown("Tweak values below to see how predictions change.")

base_drivers = get_drivers()

if base_drivers is None:
    st.error("❌ `drivers.csv` not found. Make sure it's in the same folder as `app.py`.")
    st.stop()  # Halt the app cleanly — nothing below runs

# Let the user override qualifying positions in the sidebar
edited_drivers = []
for driver in base_drivers:
    with st.sidebar.expander(driver["Driver"]):
        new_qual = st.slider(
            "Qualifying Position",
            min_value=1, max_value=20,
            value=driver["Qualifying"],
            key=f"qual_{driver['Driver']}"
        )
        new_prev = st.slider(
            "Previous Finish",
            min_value=1, max_value=20,
            value=driver["PreviousFinish"],
            key=f"prev_{driver['Driver']}"
        )
        # Build updated driver dict with user's overrides
        edited_drivers.append({
            **driver,
            "Qualifying":     new_qual,
            "PreviousFinish": new_prev,
        })

# Recalculate predictions with (potentially edited) values
ranked_drivers = predict_winner(edited_drivers)

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

tab1, tab2, tab3 = st.tabs(["📋 Full Rankings", "📊 Score Breakdown", "📈 Score Chart"])

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