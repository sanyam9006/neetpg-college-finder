import pytest
from fastapi.testclient import TestClient
from src.api.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert 800 in data["models_loaded"]


def test_predict_endpoint_800(client):
    payload = {"score": 540, "pattern": 800, "category": "UR"}
    res = client.post("/api/v1/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 540
    assert 10000 <= data["predicted_rank"] <= 15000
    assert data["min_rank"] <= data["predicted_rank"] <= data["max_rank"]
    assert data["is_qualified"] is True


def test_predict_endpoint_720(client):
    payload = {"score": 520, "pattern": 720, "category": "OBC"}
    res = client.post("/api/v1/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["max_marks"] == 720
    assert data["predicted_rank"] < 8000


def test_recommend_endpoint(client):
    payload = {"rank": 8500, "category": "UR", "state": "Delhi"}
    res = client.post("/api/v1/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "colleges" in data
    assert data["rank_evaluated"] == 8500


def test_unified_endpoint(client):
    payload = {"score": 610, "pattern": 800, "category": "UR"}
    res = client.post("/api/v1/predict-and-recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "prediction" in data
    assert "recommendation" in data
    assert data["recommendation"]["total_found"] > 0


def test_feedback_endpoint(client):
    payload = {
        "score": 550,
        "pattern": 800,
        "category": "UR",
        "predicted_rank": 10500,
        "actual_rank": 10200,
        "notes": "Official scorecard actual AIR"
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["error_ranks"] == 300


def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "neetpg_api_requests_total" in res.text


def test_feedback_input_validation(client):
    # Invalid rank exceeding bounds
    bad_payload = {
        "score": 500,
        "pattern": 800,
        "category": "UR",
        "predicted_rank": 10000,
        "actual_rank": 999999,  # exceeds 250000
        "notes": "Test invalid bounds"
    }
    res = client.post("/api/v1/feedback", json=bad_payload)
    assert res.status_code == 422  # Unprocessable Entity validation error
