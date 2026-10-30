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
    data = response.json()
    total = data['H'] + data['D'] + data['A']
    assert response.status_code == 200
    assert abs( 1 - total) < 0.01

def test_predict_same_team():
    response = client.post("/predict",json={"home_team": "Arsenal", "away_team" : "Arsenal"})
    assert response.status_code == 400

def test_predict_unknown_team():
    response = client.post("/predict",json={"home_team": "Arsnal", "away_team" : "Chelsea"})
    assert response.status_code == 404
