import fastf1
import pandas as pd
import datetime
import os

CACHE_DIR = 'cache'
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

now = pd.Timestamp(datetime.datetime.now())

for year in [2025, 2026]:
    schedule = fastf1.get_event_schedule(year)
    past_races = schedule[(schedule['EventDate'] < now) & (schedule['RoundNumber'] > 0)]
    for _, race in past_races.iterrows():
        race_name = race['EventName']
        print(f"Fetching {year} - {race_name}")
        try:
            q = fastf1.get_session(year, race_name, 'Q')
            q.load(telemetry=False, weather=True, messages=False)
            r = fastf1.get_session(year, race_name, 'R')
            r.load(telemetry=False, weather=True, messages=False)
        except Exception as e:
            print(f"Error fetching {year} {race_name}: {e}")
