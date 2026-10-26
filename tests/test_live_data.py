import json

import pytest

import live_data


def provider(path):
    results = [{'Driver': {'driverId': str(i), 'givenName': 'Driver', 'familyName': str(i)},
                'Constructor': {'name': 'McLaren'}, 'position': str(i), 'grid': str(i)} for i in range(1, 23)]
    race = {'season': '2026', 'round': '1', 'date': '2026-03-08', 'raceName': 'Source GP', 'Results': results}
    if path == 'current/last/results':
        return {'RaceTable': {'Races': [race]}}
    if 'driverStandings' in path:
        return {'StandingsTable': {'StandingsLists': [{'DriverStandings': results}]}}
    if 'qualifying' in path:
        return {'RaceTable': {'Races': []}}
    return {'RaceTable': {'Races': [race, {'round': '2', 'raceName': 'Target GP', 'date': '2026-03-15'}]}}


@pytest.fixture
def snapshot(monkeypatch, tmp_path):
    monkeypatch.delenv('VERCEL', raising=False)
    monkeypatch.setattr(live_data, 'SNAPSHOT', tmp_path / 'snapshot.json')
    monkeypatch.setattr(live_data, 'request', provider)
    return live_data.SNAPSHOT


def test_refresh_persists_complete_field_and_provisional_basis(snapshot):
    data = live_data.refresh()
    assert len(data['drivers']) == 22
    assert data['metadata']['targetRace'] == 'Target GP'
    assert data['metadata']['qualifyingBasis'] == 'Previous race grid (provisional)'
    assert json.loads(snapshot.read_text()) == data
    assert data['drivers'][0]['ChampPosition'] == 1


def test_target_qualifying_overrides_old_grid(snapshot, monkeypatch):
    def with_qualifying(path):
        if 'qualifying' in path:
            rows = provider('current/last/results')['RaceTable']['Races'][0]['Results']
            for row in rows:
                row['position'] = str(23 - int(row['position']))
            return {'RaceTable': {'Races': [{'QualifyingResults': rows}]}}
        return provider(path)
    monkeypatch.setattr(live_data, 'request', with_qualifying)
    data = live_data.refresh()
    assert data['drivers'][0]['Qualifying'] == 22
    assert data['drivers'][0]['PreviousFinish'] == 1
    assert data['metadata']['qualifyingBasis'] == 'Target race qualifying'


def test_failed_refresh_preserves_snapshot(snapshot, monkeypatch):
    data = live_data.refresh()
    data['metadata']['updatedAt'] = '2020-01-01T00:00:00+00:00'
    snapshot.write_text(json.dumps(data))
    before = snapshot.read_bytes()
    def unavailable(path):
        raise OSError('Offline')
    monkeypatch.setattr(live_data, 'request', unavailable)
    with pytest.raises(OSError):
        live_data.refresh()
    assert snapshot.read_bytes() == before


def test_incomplete_results_do_not_write(snapshot, monkeypatch):
    def incomplete(path):
        response = provider(path)
        if path == 'current/last/results':
            response['RaceTable']['Races'][0]['Results'] = []
        return response
    monkeypatch.setattr(live_data, 'request', incomplete)
    with pytest.raises(ValueError, match='incomplete'):
        live_data.refresh()
    assert not snapshot.exists()


def test_api_uses_snapshot_and_retains_data_on_failure(snapshot, monkeypatch):
    from fastapi.testclient import TestClient
    from backend import api
    live_data.refresh()
    client = TestClient(api.app)
    response = client.get('/api/predict')
    assert response.status_code == 200
    assert response.json()['totalDrivers'] == 22
    assert response.json()['metadata']['sourceRace'] == 'Source GP'
    def unavailable():
        raise OSError('Offline')
    monkeypatch.setattr(api, 'refresh', unavailable)
    assert client.post('/api/data/refresh').status_code == 503
    assert client.get('/api/predict').json() == response.json()
