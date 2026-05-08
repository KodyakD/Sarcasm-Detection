from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_analyze_success_contract() -> None:
    with TestClient(app) as client:
        response = client.post("/analyze", json={"text": "yeah right this is perfect"})

    assert response.status_code == 200
    body = response.json()
    for key in [
        "is_sarcastic",
        "confidence",
        "language",
        "sarcasm_type",
        "target",
        "intensity",
        "explanation",
        "indicators",
    ]:
        assert key in body


def test_analyze_rejects_empty_text() -> None:
    with TestClient(app) as client:
        response = client.post("/analyze", json={"text": "   "})

    assert response.status_code == 400


def test_all_requested_endpoints_are_exposed() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json")

    assert schema.status_code == 200
    paths = schema.json().get("paths", {})
    assert "/analyze" in paths
    assert "/analyze-file" in paths
    assert "/history" in paths
    assert "/health" in paths
