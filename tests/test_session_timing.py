import datetime as dt
import pytest
import session_timing as timing


@pytest.fixture
def session(monkeypatch):
    row = {'session_key': 1, 'session_name': 'Practice 1', 'session_type': 'Practice',
           'date_start': '2026-10-25T12:00:00+00:00', 'date_end': '2026-10-25T13:00:00+00:00'}
    monkeypatch.setattr(timing, 'sessions', lambda: [row])
    monkeypatch.delenv('OPENF1_ACCESS_TOKEN', raising=False)
    return row


def at(monkeypatch, value):
    monkeypatch.setattr(timing, 'now', lambda: dt.datetime.fromisoformat(value))


def test_future_session_has_no_timing_request(session, monkeypatch):
    at(monkeypatch, '2026-10-25T11:00:00+00:00')
    monkeypatch.setattr(timing, 'fetch', lambda *a, **k: pytest.fail('Future timing requested'))
    assert timing.timing(1)['status'] == 'upcoming'


def test_live_access_required_and_post_session_window(session, monkeypatch):
    at(monkeypatch, '2026-10-25T13:20:00+00:00')
    assert timing.timing(1)['status'] == 'access_required'


def test_completed_results_enriched_and_sorted(session, monkeypatch):
    at(monkeypatch, '2026-10-25T14:00:00+00:00')
    responses = {'drivers': [{'driver_number': 4, 'full_name': 'Lando Norris', 'team_name': 'McLaren'}],
                 'session_result': [{'driver_number': 4, 'position': 1, 'duration': 82.5, 'number_of_laps': 20}]}
    monkeypatch.setattr(timing, 'fetch', lambda endpoint, *a, **k: responses[endpoint])
    result = timing.timing(1)
    assert result['status'] == 'completed'
    assert result['rows'][0]['name'] == 'Lando Norris'
    assert result['rows'][0]['duration'] == 82.5


def test_stale_events_not_marked_live(session, monkeypatch):
    at(monkeypatch, '2026-10-25T12:30:00+00:00')
    monkeypatch.setenv('OPENF1_ACCESS_TOKEN', 'test-only')
    responses = {'drivers': [], 'laps': [], 'position': [{'driver_number': 4, 'position': 1, 'date': '2026-10-25T12:00:00+00:00'}]}
    monkeypatch.setattr(timing, 'fetch', lambda endpoint, *a, **k: responses[endpoint])
    assert timing.timing(1)['status'] == 'waiting'


def test_unknown_session(session):
    with pytest.raises(LookupError):
        timing.timing(999)
