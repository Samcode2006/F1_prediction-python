"""OpenF1 schedule and timing adapter. Credentials remain on the server."""
import datetime as dt
import json
import os
import threading
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_cache = {}
_lock = threading.Lock()
_last_request = 0


def now():
    return dt.datetime.now(dt.timezone.utc)


def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def fetch(endpoint, params, ttl=30):
    global _last_request
    key = (endpoint, urlencode(params))
    with _lock:
        cached = _cache.get(key)
        if cached and time.monotonic() - cached[0] < ttl:
            return cached[1]
        time.sleep(max(0, .4 - (time.monotonic() - _last_request)))
        headers = {'User-Agent': 'F1Predictor/3.0'}
        token = os.environ.get('OPENF1_ACCESS_TOKEN')
        if token:
            headers['Authorization'] = f'Bearer {token}'
        _last_request = time.monotonic()
        with urlopen(Request(f'https://api.openf1.org/v1/{endpoint}?{key[1]}', headers=headers), timeout=15) as response:
            data = json.load(response)
        _cache[key] = (time.monotonic(), data)
        return data


def sessions():
    return sorted(fetch('sessions', {'year': now().year}, ttl=300), key=lambda row: row['date_start'])


def latest_by_driver(rows):
    output = {}
    for row in sorted(rows, key=lambda item: item.get('date', '')):
        output[row['driver_number']] = row
    return output


def timing(session_key):
    session = next((s for s in sessions() if s['session_key'] == session_key), None)
    if session is None:
        raise LookupError('Session not found')
    current = now()
    start, end = timestamp(session['date_start']), timestamp(session['date_end'])
    result = {'session': session, 'rows': [], 'updatedAt': current.isoformat(), 'lastEventAt': None}
    if session.get('is_cancelled'):
        return {**result, 'status': 'cancelled'}
    if current < start:
        return {**result, 'status': 'upcoming'}
    if current < end + dt.timedelta(minutes=30) and not os.environ.get('OPENF1_ACCESS_TOKEN'):
        return {**result, 'status': 'access_required'}
    drivers = {d['driver_number']: d for d in fetch('drivers', {'session_key': session_key}, ttl=300)}
    if current >= end + dt.timedelta(minutes=30):
        rows = fetch('session_result', {'session_key': session_key}, ttl=300)
        result['status'] = 'completed' if rows else 'pending'
    else:
        positions = latest_by_driver(fetch('position', {'session_key': session_key}))
        laps = fetch('laps', {'session_key': session_key})
        rows = []
        for number, position in positions.items():
            driver_laps = [lap for lap in laps if lap['driver_number'] == number]
            durations = [lap['lap_duration'] for lap in driver_laps if lap.get('lap_duration') and not lap.get('is_pit_out_lap')]
            rows.append({**position, 'duration': min(durations) if durations else None,
                         'number_of_laps': max((lap['lap_number'] for lap in driver_laps), default=0)})
        last_event = max((row['date'] for row in positions.values()), default=None)
        result['lastEventAt'] = last_event
        result['status'] = 'live' if last_event and (current - timestamp(last_event)).total_seconds() < 90 else 'waiting'
    for row in sorted(rows, key=lambda item: item.get('position') or 999):
        driver = drivers.get(row['driver_number'], {})
        result['rows'].append({**row, 'name': driver.get('full_name', f"Car {row['driver_number']}"),
                               'team': driver.get('team_name', ''), 'colour': driver.get('team_colour') or '888888'})
    return result
