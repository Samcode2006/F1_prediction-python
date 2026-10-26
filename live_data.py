"""Refresh an atomic prediction snapshot from published Jolpica results."""
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import threading
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SNAPSHOT = Path(os.environ.get('F1_SNAPSHOT_PATH', str(Path(tempfile.gettempdir()) / 'f1_prediction_data.json') if os.environ.get('VERCEL') else str(ROOT / 'prediction_data.json')))
LOCK = threading.Lock()
BASE = 'https://api.jolpi.ca/ergast/f1'
TEAM_NAMES = {'Red Bull': 'Red Bull Racing', 'Haas F1 Team': 'Haas F1 Team',
              'RB F1 Team': 'Racing Bulls', 'Alpine F1 Team': 'Alpine',
              'Cadillac F1 Team': 'Cadillac'}


def request(path):
    with urlopen(Request(f'{BASE}/{path}/?limit=100', headers={'User-Agent': 'F1Predictor/3.0'}), timeout=20) as response:
        return json.load(response)['MRData']


def read_snapshot():
    path = SNAPSHOT
    if not path.exists() and os.environ.get('VERCEL'):
        path = ROOT / 'prediction_data.json'
    if path.exists():
        snapshot = json.loads(path.read_text(encoding='utf-8'))
        for driver in snapshot['drivers']:
            driver['Team'] = TEAM_NAMES.get(driver['Team'], driver['Team'])
        return snapshot
    return None


def refresh():
    with LOCK:
        now = dt.datetime.now(dt.timezone.utc)
        existing = read_snapshot()
        if existing and (now - dt.datetime.fromisoformat(existing['metadata']['updatedAt'])).total_seconds() < 300:
            return existing
        races = request('current/last/results')['RaceTable']['Races']
        if not races:
            raise ValueError('No published race results available. Saved data has been retained.')
        race = races[0]
        season, round_number = race['season'], int(race['round'])
        if dt.date.fromisoformat(race['date']) > now.date():
            raise ValueError('Provider returned a future race; saved data has been retained.')
        standings = request(f'{season}/{round_number}/driverStandings')['StandingsTable']['StandingsLists']
        if not standings:
            raise ValueError('Championship standings are not published yet.')
        championship = {r['Driver']['driverId']: int(r['position']) for r in standings[0]['DriverStandings']}
        schedule = request(season)['RaceTable']['Races']
        target = next((r for r in schedule if int(r['round']) == round_number + 1), None)
        qualifying = []
        if target:
            qualifying_races = request(f'{season}/{round_number + 1}/qualifying')['RaceTable']['Races']
            if qualifying_races:
                qualifying = qualifying_races[0]['QualifyingResults']
        previous = {r['Driver']['driverId']: r for r in race['Results']}
        field = qualifying or race['Results']
        if len(field) < 18:
            raise ValueError('Published field is incomplete; saved data has been retained.')
        drivers = []
        for result in field:
            driver = result['Driver']
            prior = previous.get(driver['driverId'], {})
            team = result['Constructor']['name']
            drivers.append({
                'Driver': f"{driver['givenName']} {driver['familyName']}",
                'Team': TEAM_NAMES.get(team, team),
                'Qualifying': int(result['position']) if qualifying else int(result.get('grid') or 0) or len(field),
                'PreviousFinish': int(prior.get('position', len(field))),
                'ChampPosition': championship.get(driver['driverId'], len(field)),
            })
        snapshot = {'drivers': drivers, 'metadata': {
            'source': 'Jolpica F1', 'season': season,
            'sourceRace': race['raceName'], 'sourceDate': race['date'],
            'targetRace': target['raceName'] if target else None,
            'targetDate': target['date'] if target else None,
            'qualifyingBasis': 'Target race qualifying' if qualifying else 'Previous race grid (provisional)',
            'updatedAt': now.isoformat(),
            'note': 'Rule-based ranking, not calibrated win odds. Team ratings are manual; tyres and weather are neutral. ' +
                    ('Target qualifying is available; grid penalties are not included.' if qualifying else 'Target qualifying is unavailable; the previous grid is a proxy.'),
        }}
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(dir=SNAPSHOT.parent, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as output:
                json.dump(snapshot, output, indent=2)
            os.replace(name, SNAPSHOT)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return snapshot


if __name__ == '__main__':
    print(json.dumps(refresh()['metadata'], indent=2))
