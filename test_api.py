from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}

def test_teams():
    response = client.get("/teams")
    assert response.status_code == 200
    assert "Arsenal" in response.json()["teams"]

def test_predict_valid():
    response = client.post("/predict", json={"home_team": "Arsenal", "away_team" : "Chelsea"})
    assert response.status_code == 200
    data = response.json()
    total = data['H'] + data['D'] + data['A']
    assert abs( 1 - total) < 0.01

def test_predict_same_team():
    response = client.post("/predict",json={"home_team": "Arsenal", "away_team" : "Arsenal"})
    assert response.status_code == 400

def test_predict_unknown_team():
    response = client.post("/predict",json={"home_team": "Arsnal", "away_team" : "Chelsea"})
    assert response.status_code == 404

# The fixtures tests replace get_next_round with a fake, so they don't depend on the
# fixturedownload.com site being up. We patch main.get_next_round (not fixtures.get_next_round)
# because main.py did `from fixtures import get_next_round`, which copies the name into main.
FAKE_ROUND = [
    {"RoundNumber": 11, "DateUtc": "2026-11-21 15:00:00Z", "HomeTeam": "Arsenal", "AwayTeam": "Chelsea"},
    {"RoundNumber": 11, "DateUtc": "2026-11-21 17:30:00Z", "HomeTeam": "Made Up FC", "AwayTeam": "Chelsea"},
]

def test_fixtures_upcoming(monkeypatch):
    monkeypatch.setattr("main.get_next_round", lambda: FAKE_ROUND)
    response = client.get("/fixtures/upcoming")
    assert response.status_code == 200
    data = response.json()
    assert data["round"] == 11
    assert len(data["fixtures"]) == 2
    prediction = data["fixtures"][0]["prediction"]
    assert abs(1 - (prediction["H"] + prediction["D"] + prediction["A"])) < 0.01
    # A team with no history gets a null prediction instead of breaking the whole response
    assert data["fixtures"][1]["prediction"] is None

def test_fixtures_source_down(monkeypatch):
    import requests

    def fail():
        raise requests.ConnectionError("site down")

    monkeypatch.setattr("main.get_next_round", fail)
    response = client.get("/fixtures/upcoming")
    assert response.status_code == 503
