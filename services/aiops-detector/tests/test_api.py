from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_score():
    payload = {"service": "checkout", "values": [1, 1, 1, 1, 1, 10]}
    r = client.post("/score", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "anomaly_score" in data
    assert "anomaly" in data
    assert "rca_summary" in data
